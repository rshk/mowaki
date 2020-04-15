from flask_sqlalchemy_core import FlaskSQLAlchemy

from app.config import config
from app.utils.testing import make_test_database_url

# Import the main app.db.schema package so that models get registered
# with the metadata.
from . import schema  # noqa


def get_database_url():

    if not config.DATABASE_URL:
        raise ValueError('DATABASE_URL cannot be empty')

    if config.TEST_MODE:
        if config.TEST_DATABASE_URL:
            return config.TEST_DATABASE_URL
        return make_test_database_url(config.DATABASE_URL)

    return config.DATABASE_URL


db_url = get_database_url()

db = FlaskSQLAlchemy(db_url)
