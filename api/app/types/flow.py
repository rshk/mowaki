from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import Any, NewType
from enum import Enum

FlowID = NewType("FlowID", uuid.UUID)


class Flow(BaseModel):
    """
    A flow represents an authentication process in order to achieve an
    authorization goal.
    """

    flow_id: FlowID
    goal: Any  # List of grants to be added? But this might be dynamic!
    status: Any  # PENDING | GRANTED | DENIED

    created_at: datetime
    expires_at: datetime | None

    # Challenges to be solved for this flow
    challenges: list[Any]
