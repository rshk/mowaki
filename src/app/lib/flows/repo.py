from abc import abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol

from app.lib.flows.processor import FlowProcessor
from app.types.auth.auth_flow import FlowKind


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
