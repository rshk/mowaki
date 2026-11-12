from typing import TYPE_CHECKING

from app.lib.flows.factory import FlowFactory
from app.lib.flows.types import FlowParams, FlowState

from .processor import LoginFlowProcessor


class LoginFlowFactory(FlowFactory):
    async def create(self, params: FlowParams | None = None) -> LoginFlowProcessor:
        return LoginFlowProcessor.new()

    async def load(self, state: FlowState) -> LoginFlowProcessor:
        return LoginFlowProcessor.load(state)


if TYPE_CHECKING:
    # Ensure class can be instantiated
    _: FlowFactory = LoginFlowFactory()
