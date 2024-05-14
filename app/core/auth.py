import logging

from mowaki.jwt import TokenMaker

import app.repo.users as user_repo
from app.config import get_config
from app.models.auth_info import AuthInfo
from app.models.user import User

logger = logging.getLogger(__name__)


def create_token_maker(audience):
    cfg = get_config()
    return TokenMaker(cfg.secret_key, audience=audience)


# Authentication token management ------------------------------------

# Authentication tokens are stored in the client (typically in a
# cookie or local storage, in the case of a web browser), and used to
# authenticate requests.


def get_tm_auth():
    return create_token_maker("auth")


async def get_auth_info_from_token(token: str) -> AuthInfo:
    """
    Get an AuthInfo object from an "auth" token
    """

    if not token:
        # No token -> anonymous user
        return AuthInfo.for_anonymous()

    token_data = get_tm_auth().validate(token)
    user_id = token_data["sub"]["user_id"]

    # Retrieve the current user from the database, to make sure it
    # exists and is enabled.
    user = await user_repo.get_user_by_id(user_id)

    if not user:
        logger.warning("Got token for non-existing user %s", user_id)
        return AuthInfo.for_anonymous()

    return AuthInfo.for_user(user)


def issue_auth_token_for_user(user: User) -> str:
    return get_tm_auth().issue({"user_id": user.id})


# Login token management ---------------------------------------------

# Login tokens are used to implement "magic link" login.
# A link containing the token is send to the user (typically via email).
# Once the link is visited, the login token is exchanged through the
# API for an "auth" token, which is then stored in the browser and
# used to authenticate subsequent requests.


def get_tm_login():
    return create_token_maker("login")


async def get_or_create_user_for_login_token(token: str) -> AuthInfo:
    """
    Get or create a user associated with a login token (email address)
    """

    if not token:
        # No token -> anonymous user
        return AuthInfo.for_anonymous()

    token_data = get_tm_login().validate(token)
    user_email = token_data["sub"]["email"]

    # Try and retrieve a user for this email address
    user = await user_repo.get_user_by_email(user_email)
    if user is not None:
        return AuthInfo.for_user(user)

    # If no user was found, create a new one
    user = await user_repo.create_user(email=user_email)
    return AuthInfo.for_user(user)


def issue_login_token_for_email(email: str) -> str:
    return get_tm_login().issue({"email": email})


def get_email_from_login_token(token: str) -> str:
    token_data = get_tm_login().validate(token)
    return token_data["sub"]["email"]
