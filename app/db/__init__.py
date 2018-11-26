import os

from flask_sqlalchemy_core import FlaskSQLAlchemy

# Import the main app.db.schema package so that models get registered
# with the metadata.
from . import schema  # noqa

DATABASE_URL = os.environ['DATABASE_URL']

db = FlaskSQLAlchemy(DATABASE_URL)
