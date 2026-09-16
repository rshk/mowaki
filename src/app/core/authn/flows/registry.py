from app.core.authn.flows.processor import FlowProcessorProtocol
from app.types.auth.auth_flow import FlowKind

from .email_otp_auth import PROCESSOR as EMAIL_OTP_AUTH_PROCESSOR

FLOW_PROCESSORS: dict[FlowKind, FlowProcessorProtocol] = {
    FlowKind("email-otp-auth"): EMAIL_OTP_AUTH_PROCESSOR,
}


def get_flow_processor(kind: FlowKind | str) -> FlowProcessorProtocol:
    return FLOW_PROCESSORS[FlowKind(kind)]
