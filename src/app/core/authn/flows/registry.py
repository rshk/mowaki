from app.core.authn.flows.base import BaseFlowProcessor

from .email_otp_auth import EmailOTPAuthFlowProcessor

FLOW_PROCESSORS = {
    "email-otp-auth": EmailOTPAuthFlowProcessor,
}


def get_flow_processor_class(name: str) -> type[BaseFlowProcessor]:
    return FLOW_PROCESSORS[name]
