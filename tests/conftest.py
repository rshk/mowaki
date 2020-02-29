import pytest

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

    engine = db.get_engine()

    # Clean up, in case tables were left around from a previous run.
    # This can happen if the test process was abruptly killed.
    metadata.drop_all(engine)

    metadata.create_all(engine)

    yield

    metadata.drop_all(engine)
