from datetime import UTC, datetime

from app.const import RECENT_ASSERTION_MAX_AGE
from app.exceptions import AppException
from app.types.auth import assertions
from app.types.auth.assertions import Assertion, AssertionParams
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.authz_actions import AuthzAction
from app.types.auth.authz_result import AuthzResult
from app.types.auth.session import AuthSession
from app.types.auth.trust_level import (
    TRUST_LEVEL_HIGH,
    TRUST_LEVEL_LOW,
    TRUST_LEVEL_MID,
    TRUST_LEVEL_NONE,
    TrustLevel,
)
from app.types.user import UserID

# What trust level is granted for each assertion type
GRANTED_TRUST_LEVELS = {
    assertions.EmailOTP: TRUST_LEVEL_MID,
    assertions.PasskeyAuth: TRUST_LEVEL_HIGH,
}


async def get_auth_subject_from_session(session: AuthSession) -> AuthSubject:
    """
    Create an AuthSubject() instance from a Session.
    """

    now = datetime.now(UTC)
    bld = _AuthSubjectBuilder()

    # TODO: set max_trust_level as appropriate, checking the
    # configured authentication methods for this user.

    # Note: we might want to tweak the logic here a bit once we add
    # more assertion types, so that levels can be granted based on
    # *combinations* of assertions (eg. multiple factors -> higher
    # *trust level).

    for assertion in session.assertions:
        assertion_age = assertion.created_at - now
        is_recent = assertion_age <= RECENT_ASSERTION_MAX_AGE

        if (result := _get_user_id_and_level(assertion)) is not None:
            user_id, trust = result

            bld.set_user_id(user_id)
            bld.set_current_trust_level(trust)
            if is_recent:
                bld.set_recent_trust_level(trust)

    return bld.build()


class _AuthSubjectBuilder:
    user_id: UserID | None = None
    current_trust_level: TrustLevel = TRUST_LEVEL_NONE
    recent_trust_level: TrustLevel = TRUST_LEVEL_NONE
    max_trust_level: TrustLevel = TRUST_LEVEL_NONE

    def set_user_id(self, user_id: UserID):
        if self.user_id is None:
            self.user_id = user_id
        elif self.user_id != user_id:
            raise AppException(
                "Mismatching user IDs found in assertions:"
                f" {self.user_id} ≠ {user_id}"
                " (THIS SHOULD NEVER HAPPEN)"
            )

    def set_current_trust_level(self, level: TrustLevel):
        if level > self.current_trust_level:  # noqa: PLR1730 (more readable this way)
            self.current_trust_level = level

    def set_recent_trust_level(self, level: TrustLevel):
        if level > self.recent_trust_level:  # noqa: PLR1730 (more readable this way)
            self.recent_trust_level = level

    def set_max_trust_level(self, level: TrustLevel):
        self.max_trust_level = level

    def build(self) -> AuthSubject:
        return AuthSubject(
            user_id=self.user_id,
            current_trust_level=self.current_trust_level,
            recent_trust_level=self.recent_trust_level,
            max_trust_level=self.max_trust_level,
        )


def _get_user_id_and_level(assertion: Assertion) -> tuple[UserID, TrustLevel] | None:
    """
    Get user_id and trust level from an assertion.

    If the assertion contains indication of a user_id/trust_level,
    return it as a tuple. Return None otherwise.
    """

    def _get_level(type_: type[AssertionParams]) -> TrustLevel:
        for t in type_.mro():
            try:
                return GRANTED_TRUST_LEVELS[t]
            except KeyError:
                pass
        return TRUST_LEVEL_LOW

    level = _get_level(type(assertion.params))

    match assertion.params:
        case assertions.EmailOTP(user_id=user_id) if user_id is not None:
            return (user_id, level)
        case assertions.PasskeyAuth(user_id=user_id):
            return (user_id, level)

    return None  # no match


async def check_trust_level(
    subject: AuthSubject, level: TrustLevel, recent: bool = False
):

    user_level = subject.recent_trust_level if recent else subject.current_trust_level

    if level < TRUST_LEVEL_LOW:
        return user_level >= level

    if level > subject.max_trust_level:
        return True

    return user_level >= level


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


# def create_upgrade_flow(session, scopes) -> Flow:
#     """
#     Create a flow to upgrade a session with extra grants, based on
#     scopes.
#     """
#     pass


# def update_flow(flow, responses) -> Flow:
#     """
#     Update an authorization flow with challenge responses.

#     - Add further challenges, if needed
#     - Change the flow status if a response was conclusive
#     """
#     pass


# def upgrade_session(session, flow):
#     """
#     Take a complete flow and use it to upgrade a session (?)

#     Should we just take a list of scopes instead? That were granted by
#     the flow. Also, we need access to directly upgrade the session, so
#     a new session token can be set, for example.

#     Should this function be stateful or pure?
#     """
#     pass
