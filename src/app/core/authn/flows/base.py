from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Self

from app.types.auth.auth_flow import FlowAction, FlowChallengeData, FlowState


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
    def get_challenge_data(self) -> FlowChallengeData:
        """Get challenge data to be presented to the user"""

    @abstractmethod
    async def process(self, action: FlowAction) -> FlowActionResultStatus:
        """
        Process a workflow "action", updating state.

        This method may have side effects.

        If the return value is SUCCESS or FAILED, flow will be deleted
        afterwards.
        """


class FlowActionResultStatus(Enum):
    """Result from processing a flow action"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
