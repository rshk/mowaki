class AppException(Exception):
    pass


class UninitializedResourceError(AppException):
    pass


class ObjectNotFound(AppException):
    pass


class DevFeatureDisabled(AppException):
    """A development feature is currently disabled"""
