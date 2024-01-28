from typing import Optional

import strawberry


@strawberry.type
class GenericResult:
    """
    Result response for a GraphQL operation.
    """

    ok: bool = True
    error_message: Optional[str] = None

    @classmethod
    def success(cls, **kwargs):
        return cls(ok=True, **kwargs)

    @classmethod
    def error(cls, error_message, **kwargs):
        return cls(ok=False, error_message=error_message, **kwargs)

    @classmethod
    def from_exception(cls, error: Exception, **kwargs):
        """Return a failure result from an unhandled exception.

        This method can be extended to contain extra logic, for
        example to decide which exceptions we want to pass through to
        the user.
        """

        return cls.error(error_message=str(error), **kwargs)

    @classmethod
    def bad_request(cls, **kwargs):  # 400-ish
        kwargs.setdefault("error_message", "Bad request")
        return cls.error(**kwargs)

    @classmethod
    def unauthorized(cls, **kwargs):  # 401-ish
        kwargs.setdefault("error_message", "Authentication required")
        return cls.error(**kwargs)

    @classmethod
    def forbidden(cls, **kwargs):  # 403-ish
        kwargs.setdefault("error_message", "Not authorized")
        return cls.error(**kwargs)

    @classmethod
    def not_found(cls, **kwargs):  # 404-ish
        kwargs.setdefault("error_message", "Not found")
        return cls.error(**kwargs)
