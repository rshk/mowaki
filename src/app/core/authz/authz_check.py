import inspect
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, cast

from app.core.context import get_auth_subject
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.authz_actions import AuthzAction

from .exceptions import AuthorizationError
from .result import AuthzResult


async def check_authorization(subject: AuthSubject, action: AuthzAction) -> AuthzResult:
    """
    Check if a subject is authorized to perform an action.

    THIS FUNCTION SHOULD BE "PURE" AS MUCH AS POSSIBLE; RESULTS SHOULD
    BE CACHEABLE.

    RECURSIVE LOOKUPS CAN ALSO BE USED, TO ENCOURAGE CACHEABILITY OF
    PARTIAL CHECKS -> DO WE REALLY NEED TO CACHE, IF THIS IS PURE?

    MAYBE HAVE A NON-PURE VERSION THAT CAN BE CACHED.
    BUT THEN ALSO, SOME CHECKS MIGHT REQUIRE GETTING DATA THAT COULD
    BE EXPENSIVE TO GET, OR MAKE REQUESTS TO EXTERNAL SERVICES. MAYBE
    THIS FUNCTION CANNOT BE "PURE" AFTER ALL...

    - Subject needs to contain authorization info from the session
      - Do we want it to be *tied* or *based* on the session though?
      - Only a subset of the session fields should be used for authz checks
      - Extra information might be required to make a decision

    - Action should be app-specific; probably just some data structure
      containing fields to describe stuff like the object, etc...
    """
    # Returns GRANT | DENY | REQUIRE(<scopes>)
    return AuthzResult.allow()


def get_action_from_function_call[F: Callable](
    fn: F, args: tuple[Any], kwargs: dict[str, Any]
) -> FunctionCallAction[F]:
    sig = inspect.signature(fn)
    bound = sig.bind(*args, **kwargs)
    return FunctionCallAction(fn=fn, arguments=bound.arguments)


class FunctionCallAction[F: Callable](AuthzAction):
    __slots__ = ["arguments", "fn"]

    fn: F
    arguments: dict[str, Any]

    def __init__(self, fn: F, arguments: dict[str, Any]):
        self.fn = fn
        self.arguments = arguments


def authz_checked[F: Callable[..., Awaitable]](fn: F) -> F:
    """
    Decorator to add authorization checks around a core function.
    """

    # TODO: we might want to convert this to return a class instance
    # instead, so we can expose extra functionality through "builder"
    # methods.

    @wraps(fn)
    async def wrapped(*args, **kwargs):
        action = get_action_from_function_call(fn, args, kwargs)
        subject = get_auth_subject()
        result = await check_authorization(subject, action)
        if not result.allowed:
            exc = _authz_error_from_result(result, subject, action)
            assert exc is not None
            raise exc
        return await fn(*args, **kwargs)

    return cast(F, wrapped)


def _authz_error_from_result(
    result: AuthzResult, subject: AuthSubject, action: AuthzAction
) -> AuthorizationError | None:
    if result.allowed:
        return None  # No exception

    # FIXME: we need to have some mechanism to "censor" secrets in the
    # action when we log this exception message!
    exc = AuthorizationError(f"Subject {subject} not authorized to perform: {action}")

    # TODO: it would be nice to allow functions to customize this error message to something more informative
    # Maybe just have a mapping of action -> user message?
    exc.set_user_message("FORBIDDEN")

    for fix_action in result.fix_actions:
        exc.add_fix_action(fix_action)

    return exc
