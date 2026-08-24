from __future__ import annotations

import uuid
from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any, NewType, Protocol, Self

from pydantic import Field, PlainSerializer, PlainValidator

from app.lib.models import BaseModel
from app.lib.protocols import FromDict, ToDict
from app.types.user import UserID

from .passkey_data import PasskeyID

AssertionID = NewType("AssertionID", uuid.UUID)
AssertionKind = NewType("AssertionKind", str)


class Assertion(BaseModel):
    """Authentication assertion"""

    id: AssertionID = Field(default_factory=lambda: AssertionID(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    params: Annotated[
        BaseAssertionParams,
        PlainValidator(lambda value: validate_assertion_params(value)),
        PlainSerializer(lambda value: serialize_assertion_params(value)),
    ]

    @classmethod
    def from_params(cls, params: BaseAssertionParams) -> Assertion:
        return Assertion(params=params)

    def get_assertion_text(self) -> str:
        return self.params.get_assertion_text()


def validate_assertion_params(value: Any) -> BaseAssertionParams:
    if isinstance(value, dict):
        kind = value["kind"]
        _class = ASSERTION_TYPES[kind]
        return _class.from_dict(value)

    if type(value) in ASSERTION_KIND_FROM_TYPE:
        return value

    raise TypeError(f"Unsupported type for assertion params: {value}")


def serialize_assertion_params(value: BaseAssertionParams):
    data = value.to_dict()
    data["kind"] = ASSERTION_KIND_FROM_TYPE[type(value)]
    return data


class BaseAssertionParams(FromDict, ToDict, Protocol):
    @abstractmethod
    def get_assertion_text(self) -> str:
        pass


ASSERTION_TYPES: dict[AssertionKind, type[BaseAssertionParams]] = {}
ASSERTION_KIND_FROM_TYPE: dict[type[BaseAssertionParams], AssertionKind] = {}


def register_assertion(name: str | AssertionKind):
    if isinstance(name, str):
        name = AssertionKind(name)

    def decorator(cls):
        ASSERTION_TYPES[name] = cls
        ASSERTION_KIND_FROM_TYPE[cls] = name
        return cls

    return decorator


@register_assertion("email-auth")
@dataclass
class EmailAuth(BaseAssertionParams):
    """Solved an email-based OTP challenge"""

    email_address: str

    def get_assertion_text(self) -> str:
        return f"email-auth:{self.email_address}"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(email_address=data["email_address"])

    def to_dict(self):
        return {"email_address": self.email_address}


@register_assertion("passkey-auth")
@dataclass
class PasskeyAuth(BaseAssertionParams):
    """Authenticated using a passkey"""

    passkey_id: PasskeyID
    user_id: UserID

    def get_assertion_text(self) -> str:
        return f"passkey-auth:{self.passkey_id}"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(passkey_id=data["passkey_id"], user_id=data["user_id"])

    def to_dict(self):
        return {"passkey_id": self.passkey_id, "user_id": self.user_id}
