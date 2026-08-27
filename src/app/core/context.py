import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import NewType

from app.types.auth.auth_subject import AuthSubject
from app.types.auth.session import AuthSession, SessionToken

RequestID = NewType("RequestID", uuid.UUID)


@dataclass(slots=True)
class RequestContext:
    # Current authentication session
    auth_session: AuthSession

    # Authentication subject, derived from auth_session
    auth_subject: AuthSubject

    client_info: ClientInfo = field(default_factory=lambda: ClientInfo())

    # If a new session was created, this field will be set to the new
    # session token, so it can be returned to the client (eg. via the
    # X-Set-Session-Token header).
    new_session_token: SessionToken | None = None

    # Request ID. Mostly used for logging.
    request_id: RequestID | None = field(default_factory=lambda: generate_request_id())


@dataclass(slots=True)
class ClientInfo:
    # User preferred locale, xx_XX format
    locale: str | None = None

    # User agent string, from the user agent header
    # TODO: add parsed version too?
    user_agent_string: str | None = None

    # IP Address, usually sourced from a header
    client_ip_address: str | None = None

    # Descriptive client location. Format varies based on available
    # data. Meant for user display.
    client_location: str | None = None

    # Raw client location data, as a JSON object. Exact schema depends
    # on the source.
    client_location_data: dict[str, str] | None = None


request_context = ContextVar[RequestContext]("request_context")


def get_request_context() -> RequestContext:
    return request_context.get()


def get_current_session() -> AuthSession:
    return get_request_context().auth_session


def get_auth_subject() -> AuthSubject:
    return get_request_context().auth_subject


def get_client_info() -> ClientInfo:
    return get_request_context().client_info


def generate_request_id() -> RequestID:
    return RequestID(uuid.uuid7())
