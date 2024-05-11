import logging
from typing import Any, Optional, Union

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from strawberry.asgi import GraphQL

from app.config import AppConfig, config_context, create_config_from_env
from app.core.context import CoreContext, core_context
from app.resources import initialize_resources, resources_context
from mowaki.lib.context import contextvar_contextmanager

from .auth import get_auth_info_from_request
from .context import RequestContext, get_request_context, request_context
from .loaders import Loader
from .schema import schema

logger = logging.getLogger(__name__)


class MyGraphQL(GraphQL):
    """
    Custom GraphQL (ASGI) subclass to allow providing a custom context.
    """

    async def get_context(
        self,
        request: Union[Request, WebSocket],
        response: Optional[Response] = None,
    ) -> Any:
        # Get request context from the stack
        return get_request_context()


async def build_request_context(
    request: Union[Request, WebSocket],
    response: Optional[Response] = None,
) -> RequestContext:
    """
    Build a RequestContext for the current Starlette request.
    """
    return RequestContext(
        # Preserve these
        request=request,
        response=response,
        # This ensures objects are only cached for one request
        data_loader=Loader(),
        # We can possibly forward a request_id from a HTTP header, if
        # needed to track requests across multiple applications.
        # request_id=request.headers.get("X-Request-ID")
    )


async def build_core_context_from_request_context(ctx: RequestContext) -> CoreContext:
    """
    Build a CoreContext for the request.

    This function is async to allow, for example, to run a database
    query to fetch user information to attach to the AuthInfo object.
    """

    return CoreContext(
        auth_info=await get_auth_info_from_request(ctx.request),
        # Negotiate a language parsing the Accept-Language header, if needed
        # locale=None,
    )


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set "request" and "core" contexts based on the current request.
    """

    async def dispatch(self, request, call_next):
        req_ctx = await build_request_context(request)

        with contextvar_contextmanager(request_context, req_ctx):
            core_ctx = await build_core_context_from_request_context(req_ctx)

            with contextvar_contextmanager(core_context, core_ctx):
                response = await call_next(request)

        return response


def create_app(config: AppConfig):
    """
    Create a Starlette ASGI app to serve the GraphQL API.
    """

    app = Starlette(debug=False)

    app.add_middleware(
        CORSMiddleware,
        allow_headers=["*"],
        allow_origins=["*"],
        allow_methods=["*"],
    )

    app.add_middleware(RequestContextMiddleware)

    # TODO: use configuration for setting the debug and graphiql flags.
    graphql_app = MyGraphQL(schema, debug=False, graphiql=True)

    for path in ["/", "/graphql"]:
        app.add_route(path, graphql_app)
        app.add_websocket_route(path, graphql_app)

    return app


def create_initialized_app():
    """Main entrypoint for Uvicorn"""

    cfg = create_config_from_env()
    config_context.set(cfg)

    resources = initialize_resources(cfg)
    resources_context.set(resources)

    return create_app(cfg)
