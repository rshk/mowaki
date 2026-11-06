import uuid
from abc import abstractmethod
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import NewType, Protocol

from app.lib.flows.processor import FlowProcessor

from .registry import FlowKind, FlowRegistry


class FlowRepo[FlowID](Protocol):
    @abstractmethod
    async def create(self, kind: FlowKind) -> FlowID:
        """Create a new flow"""
        yield  # type: ignore

    @asynccontextmanager
    @abstractmethod
    async def for_processing(self, flow_id: FlowID) -> AsyncGenerator[FlowProcessor]:
        """Lock for processing"""
        yield  # type: ignore

    async def delete(self, flow_id: FlowID):
        pass

    async def cleanup(self):
        """Delete completed and expired flows"""
