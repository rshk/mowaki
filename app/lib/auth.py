import base64
import functools
import logging
import os
from collections import namedtuple

import jwt
from flask import request
from jwt.exceptions import InvalidTokenError
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Unauthorized as _Unauthorized

# TODO: make this an extensible class, so the user can implement their
# choice of methods to get users / verify credentials / ...


User = namedtuple('User', 'id,username,email')


def get_user(uid):
    if uid == 1:
        return User(1, 'admin', 'admin@example.com')
    return None


def get_user_by_email(email):
    if email == 'admin@example.com':
        return User(1, 'admin', 'admin@example.com')
    return None


def verify_credentials(username, password):
    if username in ('admin', 'admin@example.com'):
        return password == 'S3cur3'
    return False


logger = logging.getLogger(__name__)

AuthInfo = namedtuple('AuthInfo', 'user')

WSRequestContext = namedtuple('WSRequestContext', 'auth_info')


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
        return super().get_headers(environ) + [(
            'WWW-Authenticate', 'Basic realm="Login Required"',
        )]


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
        return None

    try:
        atype, avalue = value.split(' ', 1)
    except ValueError:
        raise BadRequest('Malformed Authorization header')

    token_type = atype.lower()

    if token_type == 'basic':
        username, password = _parse_basic_auth(avalue)
        user = verify_credentials(username, password)
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
        jwt_data = _verify_user_jwt(avalue)

    except InvalidTokenError:
        raise Unauthorized('Bad JWT token')

    else:
        user = get_user(jwt_data['id'])
        if user is None:
            raise Unauthorized('Bad JWT token')
        return user


JWT_SECRET_KEY = os.environ['SECRET_KEY']


def _create_user_jwt(user):
    return jwt.encode({'id': user.id}, JWT_SECRET_KEY, algorithm='HS256')


def _verify_user_jwt(token):
    return jwt.decode(token.encode(), JWT_SECRET_KEY, algorithms=['HS256'])


def get_token_for_credentials(email, password):  # -> token
    if verify_credentials(email, password):
        user = get_user_by_email(email)
        return _create_user_jwt(user)
    return None


def get_socket_context(payload):
    """Get context for websockets
    """

    logger.debug('Get socket context %s', repr(payload))

    token = payload.get('authToken')
    user = None
    if token:
        user = _get_user_from_jwt(token)

    return WSRequestContext(auth_info=AuthInfo(user=user))
