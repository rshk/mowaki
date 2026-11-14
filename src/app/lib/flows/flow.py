"""
Experimental new way of defining flows
"""

from abc import abstractmethod
from typing import Protocol, Self

from app.lib.flows.constants import FlowStatus
from app.lib.flows.types import FlowAction, FlowChallenge, FlowState


class FlowStateBlock(Protocol):
    @classmethod
    @abstractmethod
    def load(cls, state: FlowState) -> Self:
        pass

    @abstractmethod
    def dump(self) -> FlowState:
        pass

    @abstractmethod
    async def execute(self, action: FlowAction) -> FlowStateBlock:
        pass

    @abstractmethod
    def get_challenge(self) -> FlowChallenge:
        pass

    @abstractmethod
    def get_status(self) -> FlowStatus:
        pass
