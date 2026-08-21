from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Self

from app.types.auth.auth_flow import FlowAction, FlowState


class BaseFlowProcessor(metaclass=ABCMeta):
    """Base for flow processor classes"""

    @classmethod
    def new(cls) -> Self:
        return cls.from_state(FlowState({}))

    @classmethod
    @abstractmethod
    def from_state(cls, state: FlowState) -> Self:
        """Construct a new instance from state"""

    @abstractmethod
    def dump_state(self) -> FlowState:
        """Serialize internal state"""

    @abstractmethod
    def get_challenge_data(self) -> FlowState:
        """Get challenge data to be presented to the user"""

    @abstractmethod
    async def process(self, action: FlowAction) -> FlowStatus:
        """
        Process a workflow "action", updating state.

        This method may have side effects.

        If the return value is SUCCESS or FAILED, flow will be deleted
        afterwards.
        """


class FlowStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
