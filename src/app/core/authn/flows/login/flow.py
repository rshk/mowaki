"""
Definition of states for the login flow
"""

from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Discriminator, EmailStr, TypeAdapter

from app import repo
from app.core.authn.exceptions import FlowProcessingError
from app.core.authn.flows.login.utils import generate_otp
from app.core.authn.session import set_current_user_id
from app.exceptions import ObjectNotFound
from app.lib.flows.flow import FailureStateBlock, FlowStateBlock, SuccessStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge, FlowState

from .utils import compose_and_send_otp_challenge_email, do_add_session_assertion

OTP_MAX_TRIES = 3


# --------------------------------------------------------------------
# Base implementation of the FlowStateBlock protocol
# --------------------------------------------------------------------


class ModelStateBlock(BaseModel, FlowStateBlock):
    """
    Base class for Pydantic-model-based flow states
    """

    @classmethod
    def load(cls, state: FlowState) -> Self:
        return cls.model_validate(state)

    def dump(self) -> FlowState:
        return FlowState(self.model_dump(mode="python"))

    def _unsupported_action(self, action: Any):
        state_type_name = self.__class__.__name__
        action_type_name = action.__class__.__name__
        return FlowProcessingError(
            f"Action {action_type_name} is not supported in state {state_type_name}"
        )


# --------------------------------------------------------------------
# Initial state
# --------------------------------------------------------------------


class InitialState(ModelStateBlock):
    kind: Literal["initial"] = "initial"

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        _action = InitialStateActionsTA.validate_python(action)

        if isinstance(_action, StartOTPAction):
            otp = generate_otp()
            email = _action.email
            await compose_and_send_otp_challenge_email(email=email, code=otp)
            return OtpPendingState(email=email, otp=otp)

        raise self._unsupported_action(_action)

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge(
            {
                "kind": "login-init",
                "actions": [
                    StartOTPAction.model_json_schema(),
                ],
            }
        )


class StartOTPAction(BaseModel):
    """Initiate email-based OTP"""

    kind: Literal["start-email-otp"] = "start-email-otp"
    email: EmailStr


# Actions available in the initial state
InitialStateActions = Annotated[StartOTPAction, Discriminator("kind")]
InitialStateActionsTA = TypeAdapter(InitialStateActions)


# --------------------------------------------------------------------
# OTP confirmation pending
# --------------------------------------------------------------------


class OtpPendingState(ModelStateBlock):
    kind: Literal["email-otp-pending"] = "email-otp-pending"

    email: str
    otp: str
    retries_left: int = OTP_MAX_TRIES

    async def execute(self, action: FlowAction) -> LoginFlowStates:
        _action = OtpResponseAction.model_validate(action)

        if _action.otp != self.otp:
            # Maximum retries exceeded -> fail
            if self.retries_left <= 0:
                return FailureStateBlock()

            # Wrong OTP, allow retrying
            return OtpPendingState(
                email=self.email,
                otp=self.otp,
                retries_left=self.retries_left - 1,
            )

        # Add assertion to indicate the current client verified
        # ownership of this email address.
        await do_add_session_assertion(self.email)

        try:
            user = await repo.user.get_by_email(self.email)

        except ObjectNotFound:
            # User does not exist (yet); ask the user whether they want to sign up
            return SignupState(email=self.email)

        # User exists: set session's "current user" from it
        await set_current_user_id(user.id)

        # TODO: if user has an associated passkey, require using it for verification
        # TODO: if user has MFA, require it for verification
        # TODO: captcha checks (reCAPTCHA or CF Turnstile)
        # TODO: if user has no MFA, prompt to add a method?

        return SuccessStateBlock()

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge(
            {
                "kind": "otp-verify",
                "actions": [
                    OtpResponseAction.model_json_schema(),
                ],
            }
        )


class OtpResponseAction(BaseModel):
    kind: Literal["otp-response"] = "otp-response"
    otp: str


# --------------------------------------------------------------------
# Sign up
# --------------------------------------------------------------------


class SignupState(ModelStateBlock):
    kind: Literal["signup"] = "signup"
    email: str

    async def execute(self, action: FlowAction) -> LoginFlowStates:
        _action = SignupStateActionsTA.validate_python(action)

        if isinstance(_action, SignupConfirmAction):
            # Create a user and mark them as authenticated

            user_id = await repo.user.create(email=self.email)

            async with repo.user.edit_metadata(user_id) as metadata:
                metadata.display_name = _action.display_name

            await set_current_user_id(user_id)

            # TODO: after successful signup, prompt to add MFA
            return SuccessStateBlock()

        if isinstance(_action, SignupRejectAction):
            # Flow was still successful, no user is to be logged in
            return SuccessStateBlock()

        raise self._unsupported_action(_action)

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge(
            {
                "kind": "signup",
                "actions": [
                    SignupConfirmAction.model_json_schema(),
                    SignupRejectAction.model_json_schema(),
                ],
            }
        )


class SignupConfirmAction(BaseModel):
    """Confirm signup"""

    kind: Literal["signup-confirm"] = "signup-confirm"
    display_name: str | None = None


class SignupRejectAction(BaseModel):
    """Reject signup"""

    kind: Literal["signup-reject"] = "signup-reject"


SignupStateActions = Annotated[
    SignupConfirmAction | SignupRejectAction, Discriminator("kind")
]
SignupStateActionsTA = TypeAdapter(SignupStateActions)


# --------------------------------------------------------------------
# Summary of flow states
# --------------------------------------------------------------------

LoginFlowStates = Annotated[
    InitialState
    | OtpPendingState
    | SignupState
    | SuccessStateBlock
    | FailureStateBlock,
    Discriminator("kind"),
]
LoginFlowStatesTA = TypeAdapter(LoginFlowStates)
