from __future__ import annotations

import dataclasses
import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
)

# Objects ------------------------------------------------------------

RP_ID = "localhost"  # Relying Party ID (Domain)
RP_NAME = "My Python App"
ORIGIN = "http://localhost:8000"

# Mock Databases
db_users: dict[str, dict] = {}  # email -> {id, email, verified, passkeys: []}
db_otps: dict[str, str] = {}  # email -> otp_code
db_challenges: dict[str, str] = {}  # user_id -> challenge_string


# Schemas ------------------------------------------------------------


class EmailSchema(BaseModel):
    email: EmailStr


class VerifyOtpSchema(BaseModel):
    email: EmailStr
    otp: str


# Helpers ------------------------------------------------------------


def generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


# Methods ------------------------------------------------------------

router = APIRouter(tags=["authentication"])


# -------------------------------------------------------------------------
# PHASE 1: EMAIL VERIFICATION
# -------------------------------------------------------------------------


@router.post("/register/start")
def start_registration(payload: EmailSchema):
    """Step 1: User submits email. Generate and 'send' OTP."""
    email = payload.email

    # Generate a secure 6-digit OTP
    otp = generate_otp()
    db_otps[email] = otp

    # NOTE: Integrate your SMTP/SendGrid library here to mail the OTP
    print(f"[EMAIL SIMULATION] To: {email} | Your OTP is: {otp}")

    return {"message": "Verification code sent to your email."}


@router.post("/register/verify-email")
def verify_email(payload: VerifyOtpSchema):
    """Step 2: Verify the OTP and create a pending user profile."""
    email = payload.email
    otp = payload.otp

    if db_otps.get(email) != otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Clean up OTP after successful verification
    del db_otps[email]

    # Create user profile if it doesn't exist
    user_id = secrets.token_hex(16)
    db_users[email] = {
        "id": user_id,
        "email": email,
        "verified": True,
        "passkeys": [],  # Will hold public keys
    }

    return {"message": "Email verified successfully.", "user_id": user_id}


# -------------------------------------------------------------------------
# PHASE 2: WEBAUTHN PASSKEY ENROLLMENT
# -------------------------------------------------------------------------


@router.post("/passkey/register/options")
def get_registration_options(payload: EmailSchema):
    """Step 3: Generate WebAuthn options for the browser to call navigator.credentials.create()"""

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # WARNING: this does not currently verify the user identity!
    # This poses a HUGE security risk in production, needs to be
    # refactored!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    user = db_users.get(payload.email)
    if not user or not user["verified"]:
        raise HTTPException(status_code=401, detail="Email must be verified first")

    # Generate server options
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user["id"],
        user_name=user["email"],
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,  # Enforces device passkeys (TouchID/FaceID/Windows Hello)
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )

    # Save the challenge temporarily to verify the upcoming browser response
    db_challenges[user["id"]] = bytes_to_base64url(options.challenge)

    # Return JSON structure directly compatible with front-end libraries
    return dataclasses.asdict(options)


@router.post("/passkey/register/verify")
def verify_passkey_registration(email: str, credential_payload: dict):
    """Step 4: Receive public key payload from browser and cryptographically verify it."""
    user = db_users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expected_challenge = db_challenges.get(user["id"])
    if not expected_challenge:
        raise HTTPException(status_code=400, detail="Missing registration challenge")

    try:
        # Validate the cryptographic signature sent back by the browser hardware
        verification = verify_registration_response(
            credential=credential_payload,
            expected_challenge=base64url_to_bytes(expected_challenge),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            require_user_verification=True,
        )

        # Save the credential details to the user record
        passkey_data = {
            "credential_id": bytes_to_base64url(verification.credential_id),
            "public_key": bytes_to_base64url(verification.credential_public_key),
            "sign_count": verification.sign_count,
        }
        user["passkeys"].append(passkey_data)

        # Clean up challenge
        del db_challenges[user["id"]]

        return {
            "status": "success",
            "message": "Passkey registered successfully. Account setup complete.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Passkey verification failed: {str(e)}"
        )


# -------------------------------------------------------------------------
# PHASE 3: SUBSEQUENT LOGIN FLOW (Passwordless)
# -------------------------------------------------------------------------


@router.post("/login/options")
def get_login_options(payload: EmailSchema):
    """Step 1 of Login: Generate options for browser navigator.credentials.get()"""
    user = db_users.get(payload.email)
    if not user or not user["passkeys"]:
        raise HTTPException(
            status_code=400, detail="No passkeys registered for this account"
        )

    options = generate_authentication_options(
        rp_id=RP_ID, user_verification=UserVerificationRequirement.REQUIRED
    )

    db_challenges[user["id"]] = bytes_to_base64url(options.challenge)
    return dataclasses.asdict(options)


@router.post("/login/verify")
def verify_login(email: str, credential_payload: dict):
    """Step 2 of Login: Validate signature with stored public key and issue session."""
    user = db_users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User profile mismatch")

    expected_challenge = db_challenges.get(user["id"])
    if expected_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found for the user")

    # Retrieve the credential object matching what the browser provided
    provided_cred_id = credential_payload.get("id")
    stored_passkey = next(
        (p for p in user["passkeys"] if p["credential_id"] == provided_cred_id), None
    )

    if not stored_passkey:
        raise HTTPException(status_code=400, detail="Unrecognized device passkey")

    try:
        verification = verify_authentication_response(
            credential=credential_payload,
            expected_challenge=base64url_to_bytes(expected_challenge),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=base64url_to_bytes(stored_passkey["public_key"]),
            credential_current_sign_count=stored_passkey["sign_count"],
            require_user_verification=True,
        )

        # Update stored signature counter to prevent replay attacks
        stored_passkey["sign_count"] = verification.new_sign_count
        del db_challenges[user["id"]]

        # NOTE: Generate your standard JWT or cookie session helper here
        return {"status": "success", "token": "MOCK_JWT_SESSION_TOKEN"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
