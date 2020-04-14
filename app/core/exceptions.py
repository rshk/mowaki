class UserError(Exception):
    """Exceptions that can be returned directly to the user"""
    pass


class AuthorizationError(UserError):
    pass


class ValidationError(UserError):
    pass
