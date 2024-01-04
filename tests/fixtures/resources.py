import pytest

from app.config import get_config
from app.resources import initialize_resources, resources_context


@pytest.fixture(scope="session", autouse=True)
def setup_resources_context(setup_config_context):
    config = get_config()
    resources = initialize_resources(config)
    with resources_context(resources):
        yield