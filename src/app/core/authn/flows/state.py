from typing import Any, Self

from pydantic import BaseModel

from app.core.authn.exceptions import FlowProcessingError
from app.lib.flows.constants import FlowStatus
from app.lib.flows.flow import FlowStateBlock
from app.lib.flows.types import FlowState


class ModelStateBlock(BaseModel, FlowStateBlock):
    """
    Base class for Pydantic-model-based flow states
    """

    @classmethod
    def load(cls, state: FlowState) -> Self:
        return cls.model_validate(state)

    def dump(self) -> FlowState:
        return FlowState(self.model_dump(mode="python"))

    def _unsupported_action(self, action: Any):
        state_type_name = self.__class__.__name__
        action_type_name = action.__class__.__name__
        return FlowProcessingError(
            f"Action {action_type_name} is not supported in state {state_type_name}"
        )

    def get_status(self) -> FlowStatus:
        return FlowStatus.IN_PROGRESS
