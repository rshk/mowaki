from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, AsyncIterable, AsyncIterator, Callable, Iterable, Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

NOT_FOUND = 404
BAD_REQUEST = 400

router = APIRouter(tags=["authentication"])


@router.post("/")
async def authenticate(response: Response, params: AuthParams) -> AuthResponse:
    pass
    # if params.flow_id is None:
    #     # Create a new flow for this request

    #     if params.session_id is not None:
    #         # Fail if session is invalid
    #         session = await storage.get_session(params.session_id)
    #         assert session is not None

    #     flow_obj = {
    #         "session_id": params.session_id,
    #         "scopes": params.scopes,
    #     }
    #     flow_id = await storage.create_flow(flow_obj)
    #     flow = await storage.get_flow(flow_id)

    # else:

    #     flow_id = params.flow_id
    #     flow = await storage.get_flow(flow_id)

    #     if params.scopes is not None:
    #         raise HTTPException(
    #             status_code=BAD_REQUEST,
    #             detail="Cannot specify scopes for an existing flow",
    #         )

    #     if params.session_id is not None:
    #         raise HTTPException(
    #             status_code=BAD_REQUEST,
    #             detail="Cannot specify session_id for an existing flow",
    #         )

    #     if params.responses is not None:
    #         # TODO: process responses
    #         pass

    # # TODO: generate new challenges based on flow state
    # # TODO: return the challenges

    # return AuthResponse(flow_id=flow_id)


class AuthParams(BaseModel):
    flow_id: str | None = None
    session_id: str | None = None
    scopes: list[Scope] | None = None
    responses: list[ChallengeResponse] | None = None


class AuthResponse(BaseModel):
    flow_id: str
    session_id: str | None = None
    status: FlowStatus = Field(default_factory=lambda: FlowStatus.PENDING)
    challenges: list[Challenge] = Field(default_factory=list)
    # scopes: list[Scope] = Field(default_factory=list)


Scope = str | dict[str, Any]


class FlowStatus(Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"


class Challenge(BaseModel):
    kind: str
    challenge_id: str
    params: dict[str, Any]


class ChallengeResponse(BaseModel):
    kind: str
    challenge_id: str
    params: dict[str, Any]


# class UsernameChallenge:
#     kind: Literal["email"]
#     challenge_id: str
#     require_email: bool = False


# class UsernameChallengeResponse:
#     kind: Literal["email"]
#     challenge_id: str
#     username: str


# Challenge = UsernameChallenge | ...


class Storage:
    """
    Handle storage of Json objects for flows and sessions
    """

    def __init__(self):
        self.flows = InMemoryDB()
        self.sessions = InMemoryDB()

    # ----------------------------------------------------------------

    async def create_flow(self, data: Any) -> str:
        return await self.flows.create(data)

    async def get_flow(self, flow_id: str) -> dict:
        return await self.flows.get(flow_id)

    @asynccontextmanager
    async def get_flow_for_update(self, flow_id) -> AsyncIterator[dict]:
        async with self.flows.get_for_update(flow_id) as flow:
            yield flow

    async def update_flow(self, flow_id: str, updater: Callable[[Any], Any]):
        return await self.flows.update(flow_id, updater)

    async def delete_flow(self, flow_id: str):
        return await self.flows.delete(flow_id)

    # ----------------------------------------------------------------

    async def create_session(self, data: Any) -> str:
        return await self.sessions.create(data)

    async def get_session(self, session_id: str) -> dict:
        return await self.sessions.get(session_id)

    @asynccontextmanager
    async def get_session_for_update(self, session_id) -> AsyncIterator[dict]:
        async with self.sessions.get_for_update(session_id) as session:
            yield session

    async def update_session(self, session_id: str, updater: Callable[[Any], Any]):
        return await self.sessions.update(session_id, updater)

    async def delete_session(self, session_id: str):
        return await self.sessions.delete(session_id)


class InMemoryDB:
    """Store objects in a dictionary, in-memory"""

    def __init__(self):
        self.objects: dict[str, dict] = {}

    async def create(self, data: Any) -> str:
        key = str(uuid.uuid4())
        self.objects[key] = data
        return key

    async def get(self, key: str) -> dict:
        return self.objects[key]

    async def list(self) -> Iterable[tuple[str, dict]]:
        return self.objects.items()

    @asynccontextmanager
    async def get_for_update(self, key) -> AsyncIterator[dict]:
        yield self.objects[key]
        # TODO: in an actual database, update object to reflect changes

    async def update(self, key: str, updater: Callable[[Any], Any]):
        async with self.get_for_update(key) as obj:
            updater(obj)

    async def delete(self, key: str):
        self.objects.pop(key, None)


storage = Storage()
