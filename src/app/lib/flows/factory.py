from abc import abstractmethod
from typing import Protocol

from app.lib.flows.types import FlowParams, FlowState

from .processor import FlowProcessor


class FlowFactory[P: FlowProcessor](Protocol):
    @abstractmethod
    async def create(self, params: FlowParams | None = None) -> P:
        """Initialize a new flow and return a Processor instance"""

    @abstractmethod
    async def load(self, state: FlowState) -> P:
        """Load state and return a Processor instance"""
