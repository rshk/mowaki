from app.lib.flows.base import FailureStateBlock, SuccessStateBlock
from app.lib.flows.docs import ActionDocs, FlowObjectDocsRegistry, StateRel
from app.lib.flows.types import FlowKind

from .login import states as login_flow

docs = FlowObjectDocsRegistry()

# --------------------------------------------------------------------
# Login flow
# --------------------------------------------------------------------

docs.document_flow(
    FlowKind("login"),
    title="Login flow",
    summary="Authenticate a user through various methods",
    states=[StateRel(login_flow.InitialState, description="Initial flow state")],
)


# Login: initial state
docs.document_state(
    login_flow.InitialState,
    title="Initial state",
    actions=[
        ActionDocs(
            login_flow.StartOTPAction,
            title="Login with email",
            states=[
                StateRel(login_flow.OtpPendingState),
            ],
        ),
        ActionDocs(
            login_flow.StartWebauthnAction,
            title="Login with passkey",
        ),
    ],
)


# Login: OTP pending state
docs.document_state(
    login_flow.OtpPendingState,
    title="Email OTP pending",
    actions=[
        ActionDocs(
            login_flow.OtpResponseAction,
            title="Validate OTP",
            states=[
                StateRel(
                    login_flow.OtpPendingState,
                    description="If OTP verification failed, remain in this "
                    "state until a number of retries is exceeded.",
                ),
                StateRel(
                    FailureStateBlock,
                    description="If OTP verification failed more than the "
                    "allowed amount of times, the flow will fail.",
                ),
                StateRel(
                    login_flow.SignupState,
                    description="On valid OTP verification, if no user "
                    "associated with the verified email exists, ask whether "
                    "to sign up a new one.",
                ),
                StateRel(
                    SuccessStateBlock,
                    description="On valid OTP verification, if a user associated "
                    "with the verified email already exists, sign them up and "
                    "complete the flow.",
                ),
            ],
        ),
    ],
)


# Login: Confirm Signup state
docs.document_state(
    login_flow.SignupState,
    title="Confirm user signup",
    description="Ask the user whether they would like to sign up",
    actions=[
        ActionDocs(
            login_flow.SignupConfirmAction,
            title="Confirm signup",
            states=[
                StateRel(
                    SuccessStateBlock,
                    description="Sign up a new user and complete the flow",
                )
            ],
        ),
        ActionDocs(
            login_flow.SignupRejectAction,
            title="Reject signup",
            states=[
                StateRel(
                    SuccessStateBlock,
                    description="Do nothing and complete the flow",
                )
            ],
        ),
    ],
)


# --------------------------------------------------------------------
# Generic states
# --------------------------------------------------------------------

docs.document_state(SuccessStateBlock, title="Flow completed successfully")

docs.document_state(FailureStateBlock, title="Flow failed")
