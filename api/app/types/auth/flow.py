import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, NewType, Self

from pydantic import BaseModel, Discriminator, Field

from app.types.auth.challenges import Challenge
from app.types.session import SessionID

AuthFlowID = NewType("AuthFlowID", uuid.UUID)


class AuthFlow[KIND](BaseModel):
    flow_id: AuthFlowID

    # Discriminator, used to dispatch flow handling logic
    kind: KIND

    # Completed flows can actually be cleaned up
    is_completed: bool = False

    # Creation date. Used to clean up expired flows
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # This allows setting a shorter expiration date for the flow
    expires_at: datetime | None = None

    # Challenges to be solved for this flow
    challenges: list[Challenge] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)


class LoginFlow(AuthFlow):
    kind: Literal["login"]


class UpgradeFlow(AuthFlow):
    kind: Literal["upgrade"]

    # Session being upgraded
    session_id: SessionID


type AuthFlowType = Annotated[LoginFlow | UpgradeFlow, Discriminator("kind")]
