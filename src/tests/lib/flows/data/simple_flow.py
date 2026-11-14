from typing import Annotated, Literal

from pydantic import Discriminator, TypeAdapter

from app.lib.flows.base import FailureStateBlock, ModelStateBlock, SuccessStateBlock
from app.lib.flows.factory import FlowFactory
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.types import FlowAction, FlowChallenge, FlowParams, FlowState


class InitialState(ModelStateBlock):
    kind: Literal["initial"] = "initial"

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        if action["kind"] == "goto-2":
            return SecondState()
        raise self._unsupported_action(action)

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge({"kind": self.kind})


class SecondState(ModelStateBlock):
    kind: Literal["state-2"] = "state-2"

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        if action["kind"] == "ok":
            return SuccessStateBlock()
        return FailureStateBlock()

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge({"kind": self.kind})


SimpleFlowStates = Annotated[
    InitialState | SecondState | SuccessStateBlock | FailureStateBlock,
    Discriminator("kind"),
]
SimpleFlowStatesTA = TypeAdapter(SimpleFlowStates)


class SimpleFlowFactory(FlowFactory):
    async def create(self, params: FlowParams | None = None) -> SimpleFlowStates:
        _ = params  # ignore
        return InitialState()

    async def load(self, state: FlowState) -> SimpleFlowStates:
        return SimpleFlowStatesTA.validate_python(state)
