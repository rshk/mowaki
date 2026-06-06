import pytest
from app.config import get_config
from app.io.resources import initialize_resources, resources_context
from app.lib.context import scoped_context


@pytest.fixture(scope="session")
def setup_resources_context(setup_config_context):
    config = get_config()
    resources = initialize_resources(config)

    with scoped_context(resources_context, resources):
        yield
