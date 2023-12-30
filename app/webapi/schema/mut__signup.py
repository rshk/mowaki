from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlencode, urljoin

import strawberry

from app.config import get_config
from app.core.auth import issue_login_token_for_email

# from app.core.notifications import compose_login_email, send_email

logger = logging.getLogger(__name__)


async def resolve_mut_signup(data: SignupData) -> SignupResult:
    """
    Sign up: send a "login" token to a specified email address
    """

    # TODO: make sure email address passes basic validation

    token = issue_login_token_for_email(data.email)
    login_url = make_login_url(token)

    logger.debug(f"Sending email to {data.email} with login link {login_url}")
    # FIXME: actually send an email with the link
    # message = compose_login_email(data.email, login_url)
    # send_email(message)

    return SignupResult(ok=True)


def make_login_url(token):
    cfg = get_config()
    args = urlencode({"token": token})
    path = f"/login?{args}"
    return urljoin(cfg.frontend_url, path)


@strawberry.input
class SignupData:
    email: str = None
    plain_text_password: Optional[str] = None


@strawberry.type
class SignupResult:
    ok: bool = True
    error_message: Optional[str] = None
