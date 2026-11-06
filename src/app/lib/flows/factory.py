from abc import abstractmethod
from typing import Protocol

from app.types.base import JSONObject

from .processor import FlowProcessor


class FlowFactory[P: FlowProcessor](Protocol):
    @abstractmethod
    async def create(self) -> P:
        """Create a new flow of this kind"""

    @abstractmethod
    async def load(self, state: JSONObject) -> P:
        """Load state to create a flow processor instance"""
