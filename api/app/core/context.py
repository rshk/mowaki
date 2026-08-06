from contextvars import ContextVar
from dataclasses import dataclass

from app.types.auth.authorization import AuthSubject
from app.types.session import AuthSession, SessionToken


@dataclass(slots=True)
class RequestContext:
    # Current authentication session
    auth_session: AuthSession

    # Authentication subject, derived from auth_session
    auth_subject: AuthSubject

    # If a new session was created, this field will be set to the new
    # session token, so it can be returned to the client (eg. via the
    # X-Set-Session-Token header).
    new_session_token: SessionToken | None = None


request_context = ContextVar[RequestContext]("request_context")


def get_request_context() -> RequestContext:
    return request_context.get()


def get_current_session() -> AuthSession:
    return get_request_context().auth_session


def get_auth_subject() -> AuthSubject:
    return get_request_context().auth_subject
