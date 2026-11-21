from typing import TYPE_CHECKING

from app.core.authn.flows.login.flow import (
    InitialState,
    LoginFlowStates,
    LoginFlowStatesTA,
)
from app.lib.flows.factory import FlowFactory
from app.lib.flows.types import FlowParams, FlowState

from ..docs import docs


class LoginFlowFactory(FlowFactory):
    async def create(self, params: FlowParams | None = None) -> LoginFlowStates:
        _ = params  # ignore
        return InitialState()

    async def load(self, state: FlowState) -> LoginFlowStates:
        return LoginFlowStatesTA.validate_python(state)


docs.document_factory(
    LoginFlowFactory,
    title="Login flow",
    summary="Authenticate a user through various methods",
).add_state(InitialState, description="Initial flow state")


if TYPE_CHECKING:
    # Ensure class is fully implemented and can be instantiated
    _: FlowFactory = LoginFlowFactory()
