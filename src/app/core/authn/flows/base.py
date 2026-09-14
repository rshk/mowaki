from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Self

from pydantic import BaseModel

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


class BaseStandardFlowProcessor[S: BaseModel, A: BaseModel](BaseFlowProcessor):
    """Base for standardized flow processors, using pydantic models"""

    __slots__ = ["state"]

    state_type: type[S]
    action_type: type[A]
    state: S

    def __init__(self, state: S):
        self.state = state

    @classmethod
    def new(cls) -> Self:
        return cls(cls.state_type())

    @classmethod
    def from_state(cls, state: FlowState) -> Self:
        _state = cls.state_type.model_validate(state)
        return cls(_state)

    def dump_state(self) -> FlowState:
        _state = self.state.model_dump(mode="json")
        return FlowState(_state)

    def get_challenge_data(self) -> FlowChallengeData:
        return FlowChallengeData({})

    async def process(self, action: FlowAction) -> FlowActionResultStatus:
        _action = self.action_type.model_validate(action)
        return await self.process_action(_action)

    @abstractmethod
    async def process_action(self, action: A) -> FlowActionResultStatus:
        pass
