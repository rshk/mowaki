import uuid
from datetime import datetime, timezone
from typing import NewType

from pydantic import BaseModel, Field

from app.types.auth.challenges import ChallengeState
from app.types.session import SessionID

AuthFlowID = NewType("AuthFlowID", uuid.UUID)
AuthFlowKind = NewType("AuthFlowKind", str)


class AuthFlow(BaseModel):
    flow_id: AuthFlowID

    # A flow can be tied to a session
    session_id: SessionID | None = None

    # Used to dispatch flow handling logic
    kind: AuthFlowKind  # Eg. "login"

    # Completed flows can actually be cleaned up
    is_completed: bool = False

    # Creation date. Used to clean up expired flows
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # This allows setting a shorter expiration date for the flow
    expires_at: datetime | None = None

    # Challenges to be solved for this flow
    challenges: list[ChallengeState] = Field(default_factory=list)
