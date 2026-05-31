from typing import Literal, NewType

from pydantic import BaseModel

ChallengeID = NewType("ChallengeID", str)


class EmailChallenge(BaseModel):
    """Request an email address"""

    challenge_id: ChallengeID
    kind: Literal["email"]


class EmailChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["email"]
    email: str


class PasswordChallenge(BaseModel):
    """Request a password"""

    challenge_id: ChallengeID
    kind: Literal["password"]


class PasswordChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["password"]
    password: str


class OobaCodeChallenge(BaseModel):
    """Out of band authentication code"""

    challenge_id: ChallengeID
    kind: Literal["ooba"]


class OobaCodeChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["ooba"]
    code: str


class OAuthChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["oauth"]
    redirect_url: str


class OAuthChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["oauth"]
    oauth_token: str
    # TODO: do we need extra fields?


class WebAuthnChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["webauthn"]
    # TODO: add webauthn parameters


class WebAuthnChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["webauthn"]
    # TODO: add webauthn fields


class TotpChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["totp"]
    # TODO: do we need to provide any fields


class TotpChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["totp"]
    code: str


class CaptchaChallenge(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["captcha"]
    captcha_url: str  # TODO: is this enough?


class CaptchaChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["captcha"]
    code: str


class SendEmailOobaChallenge(BaseModel):
    """Request an Out Of Band Authentication code to be sent"""

    challenge_id: ChallengeID
    kind: Literal["init-email-ooba"]


class SendEmailOobaChallengeResponse(BaseModel):
    challenge_id: ChallengeID
    kind: Literal["init-email-ooba"]


Challenge = (
    EmailChallenge
    | PasswordChallenge
    | OobaCodeChallenge
    | OAuthChallenge
    | WebAuthnChallenge
    | TotpChallenge
    | CaptchaChallenge
)

Response = (
    EmailChallengeResponse
    | PasswordChallengeResponse
    | OobaCodeChallengeResponse
    | OAuthChallengeResponse
    | WebAuthnChallengeResponse
    | TotpChallengeResponse
    | CaptchaChallengeResponse
)
