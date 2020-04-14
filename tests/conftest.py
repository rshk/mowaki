import pytest

from app.config import TEST_MODE
from app.core.user import UsersCore
from app.db.schema import metadata


@pytest.fixture
def db(db_schema):
    from app.db import db

    with db.transaction(autocommit=False, rollback=True):
        # By wrapping execution in a transaction that automatically
        # gets rolled back, we can avoid having to recreate the whole
        # schema for every test function run.
        yield db


@pytest.fixture(scope='session')
def db_schema():
    from app.db import db

    if not TEST_MODE:
        # ************************************************************
        # TEST_MODE is used to make sure an appropriate testing
        # database is configured, before recreating it for test data.
        # ************************************************************
        raise ValueError('TEST_MODE is not set')

    engine = db.get_engine()

    # Clean up, in case tables were left around from a previous run.
    # This can happen if the test process was abruptly killed.
    metadata.drop_all(engine)

    metadata.create_all(engine)

    yield

    metadata.drop_all(engine)


@pytest.fixture
def users_core():
    return UsersCore.for_system()
