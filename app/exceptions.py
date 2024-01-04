class AppException(Exception):
    """Base class for exceptions triggered by this app"""

    pass


class StartupError(AppException):  # Eg misconfiguration preventing the app from running
    pass


class BadRequest(AppException):  # 400-ish
    pass


class ObjectNotFound(AppException):  # 404-ish
    pass


class AccessDenied(AppException):  # 403-ish
    pass


class TemporaryFailure(AppException):
    pass
