import base64
import functools
import logging
import os
from collections import namedtuple

import jwt
from flask import request
from jwt.exceptions import InvalidTokenError
from mowaki.auth.jwt import TokenMaker
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized as _Unauthorized

from app.config import config
from app.core.auth import AuthInfo, RequestContext
from app.core.user import UsersCore

logger = logging.getLogger(__name__)
auth_tokens = TokenMaker(config.SECRET_KEY, audience='login')

users_core = UsersCore.for_system()


class Unauthorized(_Unauthorized):
    """Custom HTTP Unauthorized exception.

    It will set the ``WWW-Authenticate`` header correctly, so that
    browsers will show a dialog asking for authentication.

    This is especially useful when using GraphQLi in development mode,
    in situations where authentication is required. Just keep in mind
    that only "Basic" authorization is supported by browsers (so you
    won't be able to use Bearer).
    """

    def get_headers(self, environ=None):
        return super().get_headers(environ) + [
            ('WWW-Authenticate', 'Basic realm="Login Required"'),
            ('Content-type', 'application/json'),
        ]

    def get_body(self, environ=None):
        # TODO: add more information to response?
        return '{}'


def load_auth_info(fn):
    """View decorator to load authentication information.

    This is used to decorate the main GraphQLView exposing the GraphQL
    endpoint.

    It will parse the Authorization header to get information about
    the current authorization token (including information about the
    current user, if any).

    The authorization info is then stored on ``request.auth_info`` and
    will be made available to GraphQL resolvers as
    ``info.context.auth_info``.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        # Get authorization information from the request.
        # This usually means parsing the Authorization header.
        # This might include running database queries to ensure
        # validity of db-based tokens.
        request.auth_info = _load_authorization_from_request(request)

        return fn(*args, **kwargs)

    return wrapper


def _load_authorization_from_request(request):

    value = request.headers.get('Authorization')

    if not value:
        return AuthInfo(user=None)

    try:
        atype, avalue = value.split(' ', 1)
    except ValueError:
        raise BadRequest('Malformed Authorization header')

    token_type = atype.lower()

    if token_type == 'basic':
        username, password = _parse_basic_auth(avalue)
        user = users_core.verify_credentials(username, password)
        if not user:
            raise Unauthorized('Bad username / password')
        return AuthInfo(user=user)

    if token_type == 'bearer':
        user = _get_user_from_jwt(avalue)
        return AuthInfo(user=user)

    raise BadRequest('Unsupported authorization type')


def _parse_basic_auth(value):
    """Parse value for Basic authorization scheme.

    It is the ``username:password`` string, base64-encoded.
    """

    try:
        _decoded = base64.decodestring(value.encode()).decode()
        username, password = _decoded.split(':', 1)
    except ValueError:
        raise BadRequest('Invalid basic authorization')
    return username, password


def _get_user_from_jwt(avalue):

    try:
        jwt_data = auth_tokens.validate(avalue.encode())

    except InvalidTokenError:
        logger.warning('Invalid JWT token')
        raise Unauthorized('Bad JWT token')

    else:
        user = users_core.get(jwt_data['sub'])

        if user is None:
            logger.warning('Found token for invalid user: {}'
                           .format(jwt_data['sub']))
            raise Unauthorized('Bad JWT token')

        return user


def get_token_for_credentials(email_or_handle, password):  # -> token
    user = users_core.verify_credentials(email_or_handle, password)
    if user:
        return auth_tokens.issue(user.id).decode()
    return None


def get_socket_context(payload):
    """Get context for websockets
    """

    logger.debug('Get socket context %s', repr(payload))

    token = payload.get('authToken')
    user = None
    if token:
        user = _get_user_from_jwt(token)

    return RequestContext(auth_info=AuthInfo(user=user))
