import pytest

from app.lib.context import scoped_context
from app.lib.mailer import record_sent_emails
from app.resources import (
    initialize_resources,
    resources_context,
)


@pytest.fixture(scope="function")
def resources(config, setup_config_context):
    resources = initialize_resources(config)
    with scoped_context(resources_context, resources):
        yield resources


@pytest.fixture(scope="function")
def email_outbox():
    with record_sent_emails() as outbox:
        yield outbox
