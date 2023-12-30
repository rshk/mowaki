from __future__ import annotations

import dataclasses
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union

# from app.models.auth import AuthInfo

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.websockets import WebSocket

    from .loaders import Loader

    # from app.graphapi.loaders import Loader
    # from app.repo import Repo

_current_request_context = ContextVar("request_context")


@dataclass
class RequestContext:
    """
    Request context for Strawberry apps.

    Mainly used to pass around low-level information about the request
    (http or websocket).

    This object should only be accessed by low-level GraphQL methods,
    and *not* by core functions (which should only use information
    provided by CoreContext)
    """

    # Request / response objects from a web framework, if available.
    request: Optional[Union[Request, WebSocket]] = None
    response: Optional[Response] = None

    # GraphQL loader for Strawberry, if available
    data_loader: Optional[Loader] = None

    # Request ID, for tracking purposes
    request_id: Optional[str] = dataclasses.field(
        default_factory=lambda: str(uuid.uuid4())
    )


@contextmanager
def request_context(obj: RequestContext):
    token = _current_request_context.set(obj)
    try:
        yield obj
    finally:
        _current_request_context.reset(token)


def get_request_context() -> RequestContext:
    try:
        return _current_request_context.get()
    except LookupError:
        return None
