from __future__ import annotations

from typing import NewType

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

# Minimum trust level to consider a user authenticated
MIN_AUTHENTICATED_TRUST_LEVEL = TRUST_LEVEL_LOW
