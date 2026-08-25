class AppException(Exception):
    pass


class UninitializedResourceError(AppException):
    pass


class ObjectNotFound(AppException):
    """Expected 1 result, found 0"""


class MultipleObjectsFound(AppException):
    """Expected <=1 results, found >1"""


class DevFeatureDisabled(AppException):
    """A development feature is currently disabled"""


class ItsABug(AppException):
    """Application reached an invalid state"""
