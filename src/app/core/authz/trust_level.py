from app.types.auth import assertions
from app.types.auth.assertions import Assertion, BaseAssertionParams
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.trust_level import (
    MIN_AUTHENTICATED_TRUST_LEVEL,
    TRUST_LEVEL_HIGH,
    TRUST_LEVEL_MID,
    TRUST_LEVEL_NONE,
    TrustLevel,
)
from app.types.user import UserID

# What trust level is granted for each assertion type
GRANTED_TRUST_LEVELS_BY_ASSERTION = {
    assertions.EmailAuth: TRUST_LEVEL_MID,
    assertions.PasskeyAuth: TRUST_LEVEL_HIGH,
}


def get_trust_level_granted_by_assertion(
    type_: type[BaseAssertionParams],
) -> TrustLevel:
    """Get the trust level granted by a given assertion"""

    for t in type_.mro():
        try:
            return GRANTED_TRUST_LEVELS_BY_ASSERTION[t]
        except KeyError:
            pass
    return TRUST_LEVEL_NONE


def get_user_id_and_level_from_assertion(
    assertion: Assertion,
) -> tuple[UserID, TrustLevel] | None:
    """
    Get user_id and trust level from an assertion.

    If the assertion contains indication of a user_id/trust_level,
    return it as a tuple. Return None otherwise.
    """

    level = get_trust_level_granted_by_assertion(type(assertion.params))

    match assertion.params:
        case assertions.EmailAuth(user_id=user_id) if user_id is not None:
            return (user_id, level)
        case assertions.PasskeyAuth(user_id=user_id):
            return (user_id, level)

    return None  # no match


async def check_trust_level(
    subject: AuthSubject, level: TrustLevel, recent: bool = False
):
    """
    Check whether a subject has at least a given trust level

    For authenticated users (TRUST_LEVEL_LOW and above), return True
    even if the requested level is not met, but authentication was
    already performed at the highest level configured for the user.

    This is useful, for example, to allow a user who only has Email
    OTP authentication to register their first passkey or MFA for the
    account. Once they enrolled in MFA, the higher authentication
    level will be required for further account actions.

    Args:

        subject:
            the subject we're checking

        level:
            minimum required level

        recent:
            Whether to require that the trust level was gained
            "recently" (see RECENT_ASSERTION_MAX_AGE).

    Returns:
        True if the trust level is met, False otherwise.
    """

    user_level = subject.recent_trust_level if recent else subject.current_trust_level

    if level < MIN_AUTHENTICATED_TRUST_LEVEL:
        return user_level >= level

    if level > subject.max_trust_level:
        return True

    return user_level >= level
