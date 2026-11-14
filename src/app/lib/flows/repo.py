from abc import abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import NamedTuple, Protocol

from app.lib.flows.flow import FlowStateBlock

from .types import FlowKind, FlowParams


class LockedFlow[FlowObject](NamedTuple):
    info: FlowObject
    state: FlowStateBlock


class FlowRepo[FlowID, FlowObject](Protocol):
    @abstractmethod
    async def create(self, kind: FlowKind, params: FlowParams | None = None) -> FlowID:
        """Create a new flow"""
        yield  # type: ignore

    @abstractmethod
    async def get(self, flow_id: FlowID) -> FlowObject:
        pass

    @asynccontextmanager
    @abstractmethod
    async def for_processing(
        self, flow_id: FlowID
    ) -> AsyncGenerator[LockedFlow[FlowObject]]:
        """
        Retrieve a flow, locking it for processing.

        Once processing is done, the flow will be updated with state
        from the processor.
        """
        yield  # type: ignore

    async def delete(self, flow_id: FlowID):
        pass

    async def cleanup(self):
        """Delete completed and expired flows"""
