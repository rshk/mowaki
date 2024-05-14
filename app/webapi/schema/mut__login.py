from __future__ import annotations

import logging
from typing import Optional

import strawberry

import app.repo.users as user_repo
from app.core.auth import get_email_from_login_token, issue_auth_token_for_user

logger = logging.getLogger(__name__)


async def resolve_mut_login(token: str) -> LoginResult:
    # Try and get a user for this token

    email = get_email_from_login_token(token)
    logger.debug("Logging in user with email: %s", email)

    user = await user_repo.get_user_by_email(email)

    if user is None:
        logger.info("Creating new user with email: %s", email)
        user_id = await user_repo.create_user(email=email)
        user = await user_repo.get_user_by_id(user_id)

    else:
        logger.info("Logging in existing user: %s", user.id)

    # TODO: update last login date for the user

    token = issue_auth_token_for_user(user)
    return LoginResult(ok=True, token=token)


@strawberry.type
class LoginResult:
    ok: bool = True
    token: Optional[str] = None
    error_message: Optional[str] = None
