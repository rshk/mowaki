from abc import abstractmethod
from typing import Protocol, Self

from .constants import FlowStatus
from .types import FlowAction, FlowChallenge, FlowState


class FlowProcessor(Protocol):
    @abstractmethod
    async def execute(self, action: FlowAction):
        """Execute an action"""

    @abstractmethod
    def get_challenge(self) -> FlowChallenge:
        """Get challenge parameters to be presented to the user"""

    @classmethod
    @abstractmethod
    def load(cls, state: FlowState) -> Self:
        """Create instance with state"""

    @abstractmethod
    def dump(self) -> FlowState:
        """Dump state from this processor"""

    @abstractmethod
    def get_status(self) -> FlowStatus:
        """Get status for the current flow"""
