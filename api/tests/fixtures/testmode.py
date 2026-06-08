import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_mode():
    import email_validator
    email_validator.TEST_ENVIRONMENT = True
