from collections import namedtuple

# Flask-compatible request object, to be used as graphql "context" by
# websockets and non-flask requests.
RequestContext = namedtuple('RequestContext', 'auth_info')


class AuthInfo:

    def __init__(self, *, user, is_system=False):
        """Authorization info

        Used for checking request authorization.

        Args:

            user:
                User object, or None if not authenticated

            is_system:
                Set to True for "system" usage (eg. the CLI).
                Grants complete access to everything.
        """
        self.user = user
        self.is_system = is_system

    @classmethod
    def for_user(cls, user):
        return cls(user=user)

    @classmethod
    def for_anonymous(cls):
        return cls(user=None)

    @classmethod
    def for_system(cls):
        return cls(user=None, is_system=True)

    def is_authenticated(self):
        return bool(self.user)

    def is_superuser(self):
        return self.is_system

    def can_admin_users(self):
        return self.is_superuser()

    def __repr__(self):
        if self.is_system:
            if self.user:
                return '<AuthInfo SYSTEM (UID={})>'.format(self.user.id)
            return '<AuthInfo SYSTEM>'

        if self.user:
            return '<AuthInfo USER={}>'.format(self.user.id)

        return '<AuthInfo ANONYMOUS>'
