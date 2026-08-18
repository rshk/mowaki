from app.types.auth.authorization import AuthSubject, AuthzAction, AuthzResult


def check_authorization(subject: AuthSubject, action: AuthzAction) -> AuthzResult:
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
