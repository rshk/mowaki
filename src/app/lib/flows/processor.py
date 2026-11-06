from abc import abstractmethod
from typing import Protocol, Self

from app.types.base import JSONObject

from .constants import FlowStatus


class FlowProcessor(Protocol):
    @abstractmethod
    async def execute(self, action: JSONObject):
        """Execute an action"""

    @abstractmethod
    def get_challenge(self) -> JSONObject:
        """Get challenge parameters to be presented to the user"""

    @classmethod
    @abstractmethod
    def load(cls, state: JSONObject) -> Self:
        """Create instance with state"""

    @abstractmethod
    def dump(self) -> JSONObject:
        """Dump state from this processor"""

    @abstractmethod
    def get_status(self) -> FlowStatus:
        """Get status for the current flow"""
