from __future__ import annotations

# Authorization actions ----------------------------------------------


class AuthzAction:
    """Base for objects representing application actions.

    Used for authorization checks.  Subclasses are
    application-specific.
    """

    # Leave it to the app to implement actions.
    # This can even be Union, or Protocol
