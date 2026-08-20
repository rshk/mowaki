from app.core.context import get_current_session
from app.types.auth.auth_flow import EmailOTPAuthFlowState, FlowID, FlowState


async def create_flow(state: FlowState) -> FlowID:
    # TODO: use repo to store flow to database
    pass


async def process_flow():
    pass


async def delete_flow():
    pass


async def cleanup_completed_flows():
    pass
