from app.exceptions import AppException


class SessionError(AppException):
    pass


class SessionExpired(SessionError):
    """Session was found, but it expired"""


class SessionNotFound(SessionError):
    """Session was not found"""


class SessionInvalid(SessionError):
    """Session was found but it's invalid for some reason"""


class FlowExpired(AppException):
    pass


class FlowAccessDenied(AppException):
    pass


class FlowAlreadyCompleted(AppException):
    pass


class FlowProcessingError(AppException):
    pass
