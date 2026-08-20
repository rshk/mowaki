import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal, NewType

from pydantic import Discriminator, Field, TypeAdapter

from app.lib.models import BaseModel
from app.types.auth.session import SessionID

FlowID = NewType("FlowID", uuid.UUID)


class AuthFlow(BaseModel):
    """Authentication flow"""

    flow_id: FlowID = Field(default_factory=lambda: FlowID(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    session_id: SessionID | None = None
    state: FlowState
    is_completed: bool = False


class EmailOTPAuthFlowState(BaseModel):
    """Authenticate with email OTP"""

    kind: Literal["email-otp-auth"] = Field(default="email-otp-auth")
    email_address: str
    otp_code: str


class EmailOTPRefreshFlowState(BaseModel):
    """Refresh an existing email OTP assertion"""

    kind: Literal["email-otp-refresh"] = Field(default="email-otp-refresh")
    email_address: str
    otp_code: str


class EmailOTPEnrollFlowState(BaseModel):
    """Add a new verified email address"""

    kind: Literal["email-otp-enroll"] = Field(default="email-otp-enroll")
    email_address: str
    otp_code: str


class SignupFlowState(BaseModel):
    """Create a new account, based on session assertions"""

    kind: Literal["signup"] = Field(default="signup")


# class PasskeyAuthFlowState(BaseModel):
#     """Authenticate with a passkey"""

#     kind: Literal["passkey-auth"] = Field(default="passkey-auth")


# class PasskeyRefreshFlowState(BaseModel):
#     """Refresh an existing passkey assertion"""

#     kind: Literal["passkey-auth"] = Field(default="passkey-auth")


# class PasskeyEnrollFlowState(BaseModel):
#     """Add a new passkey to an account"""

#     kind: Literal["passkey-enroll"] = Field(default="passkey-enroll")


# class TOTPAuthFlowState(BaseModel):
#     """Provide code from TOTP authenticator"""

#     kind: Literal["totp-auth"] = Field(default="totp-auth")


# class TOTPEnrollFlowState(BaseModel):
#     """Enroll a new TOTP authenticator"""

#     kind: Literal["totp-enroll"] = Field(default="totp-enroll")


FlowState = Annotated[
    EmailOTPAuthFlowState
    | EmailOTPRefreshFlowState
    | EmailOTPEnrollFlowState
    | SignupFlowState,
    Discriminator("kind"),
]

FlowStateTA = TypeAdapter(FlowState)
