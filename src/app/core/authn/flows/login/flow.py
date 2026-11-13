"""
Definition of flow states
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, Discriminator, EmailStr, TypeAdapter

from app.core.authn.exceptions import FlowProcessingError
from app.core.authn.flows.login.utils import generate_otp
from app.lib.flows.flow import FailureStateBlock, FlowStateBlock, SuccessStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge, FlowState

from .utils import compose_and_send_otp_challenge_email, do_add_session_assertion

# --------------------------------------------------------------------
# Base implementation of the FlowStateBlock protocol
# --------------------------------------------------------------------


class LoginStateBlock(BaseModel, FlowStateBlock):
    @classmethod
    def load(cls, state: FlowState) -> Self:
        return cls.model_validate(state)

    def dump(self) -> FlowState:
        return FlowState(self.model_dump(mode="python"))


# --------------------------------------------------------------------
# Initial state
# --------------------------------------------------------------------


class InitialState(LoginStateBlock):
    kind: Literal["initial"] = "initial"

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        _action = InitialStateActionsTA.validate_python(action)

        if isinstance(_action, StartOTPAction):
            otp = generate_otp()
            email = _action.email
            await compose_and_send_otp_challenge_email(email=email, code=otp)
            return OtpPendingState(email=email, otp=otp)

        raise FlowProcessingError("Unsupported flow action in this state")

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


class OtpPendingState(LoginStateBlock):
    kind: Literal["email-otp-pending"] = "email-otp-pending"

    email: str
    otp: str
    retries_left: int = 3

    async def execute(self, action: FlowAction) -> LoginFlowStates:
        _action = OtpResponseAction.model_validate(action)

        if _action.otp != self.otp:
            if self.retries_left <= 0:
                return FailureStateBlock()
            return OtpPendingState(
                email=self.email, otp=self.otp, retries_left=self.retries_left - 1
            )

        await do_add_session_assertion(self.email)

        # FIXME: return next state in the flow instead!
        return SuccessStateBlock()

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge(
            {"kind": "otp-response", "actions": [OtpResponseAction.model_json_schema()]}
        )


class OtpResponseAction(BaseModel):
    kind: Literal["otp-response"] = "otp-response"
    otp: str


# --------------------------------------------------------------------
# Summary of flow states
# --------------------------------------------------------------------

LoginFlowStates = Annotated[
    InitialState | OtpPendingState | SuccessStateBlock | FailureStateBlock,
    Discriminator("kind"),
]
LoginFlowStatesTA = TypeAdapter(LoginFlowStates)
