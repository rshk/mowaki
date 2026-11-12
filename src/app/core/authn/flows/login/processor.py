from typing import Self

from app.core.authn.exceptions import FlowProcessingError
from app.core.authn.flows.login.types import (
    ActionTypeAdapter,
    ChallengeType,
    EmailAddrAction,
    EmailOtpChallenge,
    InitialChallenge,
    LoginFlowState,
    OtpAction,
)
from app.exceptions import ItsABug
from app.lib.flows.constants import FlowStatus
from app.lib.flows.processor import FlowProcessor
from app.lib.flows.types import FlowAction, FlowChallenge, FlowParams, FlowState

from .utils import (
    compose_and_send_otp_challenge_email,
    do_add_session_assertion,
    generate_otp_code,
)


class LoginFlowProcessor(FlowProcessor):
    def __init__(self, state: LoginFlowState):
        self._state = state
        self._status = FlowStatus.IN_PROGRESS

    @classmethod
    def new(cls, params: FlowParams | None = None) -> Self:
        state = LoginFlowState()
        return cls(state)

    async def execute(self, action: FlowAction):
        action = ActionTypeAdapter.validate_python(action)

        # STEP 1: get email address -> generate and send OTP code

        if self._state.email is None:
            if isinstance(action, EmailAddrAction):
                _email = action.email
                _code = generate_otp_code()
                await compose_and_send_otp_challenge_email(_email, _code)

                self._state.email = _email
                self._state.otp = _code
                return

            raise FlowProcessingError("Unsupported action in this state")

        # STEP 2: verify OTP code

        if self._state.otp is None:
            # This should never happen
            raise ItsABug("Missing OTP code from state of in-progress login flow")

        # User provided an OTP for verification

        if isinstance(action, OtpAction):
            if action.otp == self._state.otp:
                # SUCCESS: user provided a valid OTP
                # Grant new assertion to the session
                await do_add_session_assertion(self._state.email)
                self._status = FlowStatus.COMPLETED
                return

            else:
                # FAILED -> wrong OTP code
                self._status = FlowStatus.FAILED
                return

    def get_challenge(self) -> FlowChallenge:
        challenge = self._get_challenge()
        return FlowChallenge(challenge.model_dump(mode="python"))

    def _get_challenge(self) -> ChallengeType:
        if self._state.email is None:
            return InitialChallenge(
                email_auth_available=True,
                webauthn_available=False,
                actions=[
                    EmailAddrAction.model_json_schema(),
                ],
            )

        assert self._state.otp is not None

        return EmailOtpChallenge(
            actions=[
                OtpAction.model_json_schema(),
            ]
        )

    @classmethod
    def load(cls, state: FlowState) -> Self:
        _state = LoginFlowState.model_validate(state)
        return cls(_state)

    def dump(self) -> FlowState:
        data = self._state.model_dump(mode="python")
        return FlowState(data)

    def get_status(self) -> FlowStatus:
        return self._status
