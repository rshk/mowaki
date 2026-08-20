from datetime import UTC, datetime

from app.const import RECENT_ASSERTION_MAX_AGE
from app.core.authz.trust_level import get_user_id_and_level_from_assertion
from app.exceptions import AppException
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.session import AuthSession
from app.types.auth.trust_level import (
    TRUST_LEVEL_NONE,
    TrustLevel,
)
from app.types.user import UserID


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

        if (result := get_user_id_and_level_from_assertion(assertion)) is not None:
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
