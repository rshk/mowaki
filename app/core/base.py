from .auth import AuthInfo, RequestContext

from .exceptions import AuthorizationError


class BaseCore:

    def __init__(self, context):
        self.context = context

    @classmethod
    def from_request(cls, request=None):
        if request is None:
            import flask
            request = flask.request
        return cls(request)

    @classmethod
    def for_user(cls, user):
        """Instantiate core for a specific user"""
        return cls(RequestContext(auth_info=AuthInfo.for_user(user)))

    @classmethod
    def for_anonymous(cls):
        """Instantiate core for a non-authenticated user"""
        return cls(RequestContext(auth_info=AuthInfo.for_anonymous()))

    @classmethod
    def for_system(cls):
        """Instantiate core for the "system" (full privileges, no user)"""
        return cls(RequestContext(auth_info=AuthInfo.for_system()))

    def get_auth_info(self) -> AuthInfo:
        return self.context.auth_info

    def get_current_user(self, require=False):
        user = self.context.auth_info.user
        if require and (not user):
            raise AuthorizationError('Authentication is required')
        return user
