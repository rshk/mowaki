"""
Experimental new way of defining flows
"""

from abc import abstractmethod
from typing import Protocol, Self

from app.core.authn.exceptions import FlowProcessingError
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


class SuccessStateBlock(FlowStateBlock):
    @classmethod
    def load(cls, state: FlowState) -> Self:
        return cls()

    def dump(self) -> FlowState:
        return FlowState({"kind": "success"})

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        raise FlowProcessingError("Flow is already completed")

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge({"kind": "final", "status": "completed"})


class FailureStateBlock(FlowStateBlock):
    @classmethod
    def load(cls, state: FlowState) -> Self:
        return cls()

    def dump(self) -> FlowState:
        return FlowState({"kind": "failure"})

    async def execute(self, action: FlowAction) -> FlowStateBlock:
        raise FlowProcessingError("Flow is already failed")

    def get_challenge(self) -> FlowChallenge:
        return FlowChallenge({"kind": "final", "status": "failed"})
