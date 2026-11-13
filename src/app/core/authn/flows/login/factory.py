from typing import TYPE_CHECKING

from app.core.authn.flows.login.flow import (
    InitialState,
    LoginFlowStates,
    LoginFlowStatesTA,
)
from app.core.authn.flows.login.sidefx import LoginSideFxProto
from app.lib.flows.factory import FlowFactory
from app.lib.flows.types import FlowParams, FlowState


class LoginFlowFactory(FlowFactory):
    def __init__(self, deps: LoginSideFxProto | None = None):
        self._deps = deps

    async def create(self, params: FlowParams | None = None) -> LoginFlowStates:
        _ = params  # ignore
        return InitialState()

    async def load(self, state: FlowState) -> LoginFlowStates:
        return LoginFlowStatesTA.validate_python(state)


if TYPE_CHECKING:
    # Ensure class is fully implemented and can be instantiated
    _: FlowFactory = LoginFlowFactory()
