from abc import abstractmethod
from typing import Protocol, Self

from .constants import FlowStatus
from .types import FlowAction, FlowChallenge, FlowParams, FlowState


class FlowProcessor(Protocol):
    @classmethod
    @abstractmethod
    def new(cls, params: FlowParams | None = None) -> Self:
        pass

    @abstractmethod
    async def execute(self, action: FlowAction):
        """
        Execute an action, usually modifying the flow state.

        Action execution may have side effects.
        """

    @abstractmethod
    def get_challenge(self) -> FlowChallenge:
        """Get challenge parameters to be presented to the user"""

    @classmethod
    @abstractmethod
    def load(cls, state: FlowState) -> Self:
        """Create a processor instance from state"""

    @abstractmethod
    def dump(self) -> FlowState:
        """Dump state from this processor"""

    @abstractmethod
    def get_status(self) -> FlowStatus:
        """Get status for the current flow"""
