from __future__ import annotations

from dataclasses import dataclass

from app.types.user import UserID

from .trust_level import TRUST_LEVEL_NONE, TrustLevel


@dataclass(slots=True)
class AuthSubject:
    """
    Authorization Subject

    Represents a user of the application.
    Can be associated with a "user" or some other entity.
    Can have associated permissions, usually derived from
    authentication assertions.
    """

    # If this subject is tied to an application user, this field will
    # contain its user ID
    user_id: UserID | None = None

    # Trust level ----------------------------------------------------

    # Trust level is defined as "how much we trust this session to
    # belong to the specified user"

    # Trust level based on current assertions.
    current_trust_level: TrustLevel = TRUST_LEVEL_NONE

    # Trust level based on recent assertions.
    # An assertion is considered "recent" if not older than
    # RECENT_ASSERTION_MAX_AGE.
    recent_trust_level: TrustLevel = TRUST_LEVEL_NONE

    # Maximum trust level configured for this user.
    # Ideally this should always be TRUST_LEVEL_HIGH, but might be
    # lower if the user hasn't added any MFA / passkeys to their
    # account, for example.
    max_trust_level: TrustLevel = TRUST_LEVEL_NONE
