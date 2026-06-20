import uuid
from pydantic import BaseModel
from typing import Any, NewType

FlowID = NewType("FlowID", uuid.UUID)


class Flow(BaseModel):
    flow_id: FlowID
    # session_id: SessionID
    # scopes: list[Any]
    # challenges: list[Any]
