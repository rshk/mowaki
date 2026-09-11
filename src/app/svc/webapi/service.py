import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from pydantic.main import BaseModel

from app.config import load_config
from app.const import CUSTOM_HEADERS, SESSION_TOKEN_HEADER
from app.core.authn.exceptions import SessionNotFound
from app.core.authn.session import create_session, get_session_from_token
from app.core.authz.exceptions import AuthorizationError
from app.core.context import RequestContext, request_context
from app.lib.context import scoped_context
from app.resources import initialize_resources
from app.types.auth.auth_subject import AuthSubject
from app.types.auth.session import AuthSession, SessionToken

from .app import create_app

# Setup logging ------------------------------------------------------

# TODO: consider switching to something more modern, like logbook
# https://logbook.readthedocs.io/en/stable/

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.addHandler(logging_handler)
root_logger.setLevel(logging.INFO)

app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)


# Initialize configuration and resources -----------------------------

config = load_config()
resources = initialize_resources(config, set_context=True)


# Create FastAPI app -------------------------------------------------

app = create_app()
