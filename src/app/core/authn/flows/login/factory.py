from typing import TYPE_CHECKING

from app.lib.flows.factory import FlowFactory
from app.lib.flows.types import FlowParams, FlowState

from .states import (
    InitialState,
    LoginFlowStates,
    LoginFlowStatesTA,
)


class LoginFlowFactory(FlowFactory):
    async def create(self, params: FlowParams | None = None) -> LoginFlowStates:
        _ = params  # ignore
        return InitialState()

    async def load(self, state: FlowState) -> LoginFlowStates:
        return LoginFlowStatesTA.validate_python(state)


if TYPE_CHECKING:
    # Ensure class is fully implemented and can be instantiated
    _: FlowFactory = LoginFlowFactory()
