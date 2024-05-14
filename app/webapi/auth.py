import logging
from typing import Union

from starlette.requests import Request
from starlette.websockets import WebSocket

from app.core.auth import get_auth_info_from_token
from app.models.auth_info import AuthInfo

logger = logging.getLogger(__name__)


async def get_auth_info_from_request(request: Union[Request, WebSocket]) -> AuthInfo:
    """Create an AuthInfo object from a Starlette request object.

    An authentication token is obtained from the HTTP Authorization
    header, if passed. Only "bearer" authentication is supported at
    the moment.

    This is an async function to allow running side effects,
    eg. database queries, to validate the token and retrieve user
    information.
    """

    header_value = request.headers.get("Authorization")

    if not header_value:
        return AuthInfo()

    try:
        atype, avalue = header_value.split(" ", 1)
    except ValueError:
        logger.warning("Malformed authorization header: %s", header_value)
        raise ValueError("Malformed authorization header")

    token_type = atype.lower()
    if token_type == "bearer":
        return await get_auth_info_from_token(avalue)

    raise ValueError(f"Unsupported authentication type: {atype}")
