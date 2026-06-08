class BaseAppException(Exception):
    pass


class UninitializedResourceError(BaseAppException):
    pass


class ObjectNotFound(BaseAppException):
    pass
