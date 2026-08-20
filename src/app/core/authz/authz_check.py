from app.types.auth.auth_subject import AuthSubject
from app.types.auth.authz_actions import AuthzAction
from app.types.auth.authz_result import AuthzResult


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
