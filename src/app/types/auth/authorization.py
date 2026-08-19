"""
Authorization-related types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, NewType

from app.types.user import UserID

TrustLevel = NewType("TrustLevel", int)

TRUST_LEVEL_NONE = TrustLevel(0)
TRUST_LEVEL_WEAK = TrustLevel(5)

# Minimum level at which a user is considered "authenticated".
# This is usually granted for phone OTP or password-only authentication.
TRUST_LEVEL_LOW = TrustLevel(10)

# Medium trust level, usually granted for solving an email OTP challenge.
TRUST_LEVEL_MID = TrustLevel(20)

# Highest trust level, granted when multi-factor authentication was
# used, or the user logged in using a passkey.
TRUST_LEVEL_HIGH = TrustLevel(50)  # MFA / passkey login

# How old an assertion can be to be considered "recent"
RECENT_ASSERTION_MAX_AGE = timedelta(minutes=5)


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


# Authorization actions ----------------------------------------------


class AuthzAction:
    """Base for objects representing application actions.

    Used for authorization checks.  Subclasses are
    application-specific.
    """

    # Leave it to the app to implement actions.
    # This can even be Union, or Protocol


# Authorization result -----------------------------------------------


@dataclass(slots=True)
class AuthzResult:
    """Result of an authorization check"""

    allowed: bool
    corrective_actions: list[BaseCorrectiveAction] = field(default_factory=list)

    @classmethod
    def allow(cls):
        return cls(allowed=True)

    @classmethod
    def deny(cls, corrective_actions: list[Any] | None = None):
        if corrective_actions is None:
            corrective_actions = []
        return cls(allowed=False, corrective_actions=corrective_actions)


class BaseCorrectiveAction:
    """Base object for "corrective actions".

    Corrective actions represent actions that can be taken to remedy a
    failed authorization attempt.
    """
