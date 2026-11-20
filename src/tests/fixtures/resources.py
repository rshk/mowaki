from collections.abc import Generator
from email.message import Message

import pytest

from app.lib.context import scoped_context
from app.lib.mailer import record_sent_emails
from app.lib.resources import ResourcesRegistry
from app.resources import (
    initialize_resources,
    resources_context,
)


@pytest.fixture(scope="function")
def resources(config, setup_config_context) -> Generator[ResourcesRegistry]:
    _ = setup_config_context  # silence linter warning
    resources = initialize_resources(config)
    with scoped_context(resources_context, resources):
        yield resources


@pytest.fixture(scope="function")
def email_outbox() -> Generator[list[Message]]:
    with record_sent_emails() as outbox:
        yield outbox
