import os

from flask_sqlalchemy_core import FlaskSQLAlchemy

from app.config import config

# Import the main app.db.schema package so that models get registered
# with the metadata.
from . import schema  # noqa

db_url = config.DATABASE_URL if not config.TEST_MODE else config.TEST_DATABASE_URL
db = FlaskSQLAlchemy(db_url)

