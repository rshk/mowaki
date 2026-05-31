"""
AuthN/Z handler
"""

from typing import Any

from api.app.types.flow import Flow, FlowID
from api.app.types.session import SessionID


class Authorizer:
    async def create_flow(
        self,
        session_id: SessionID | None = None,
        scopes: list[Any] | None = None,
    ) -> Flow:
        pass

    async def get_flow(self, flow_id: FlowID) -> Flow:
        pass

    async def update_flow(self, flow_id: FlowID, responses: list[Any]) -> Flow:
        pass
