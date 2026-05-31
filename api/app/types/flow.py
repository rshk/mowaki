from pydantic import BaseModel
from typing import Any, NewType

from api.app.types.session import SessionID

FlowID = NewType("FlowID", str)


class Flow(BaseModel):
    flow_id: FlowID
    session_id: SessionID
    scopes: list[Any]
    challenges: list[Any]
