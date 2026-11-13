from abc import abstractmethod
from typing import Protocol

from app.lib.flows.types import FlowParams, FlowState

from .flow import FlowStateBlock


class FlowFactory(Protocol):
    @abstractmethod
    async def create(self, params: FlowParams | None = None) -> FlowStateBlock:
        """Initialize flow state"""

    @abstractmethod
    async def load(self, state: FlowState) -> FlowStateBlock:
        """Load flow state"""
