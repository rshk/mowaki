from collections.abc import AsyncGenerator

import pytest_asyncio

from tests.utils.session import TestingRequestContextManager


@pytest_asyncio.fixture
async def request_ctx_manager(database_schema) -> TestingRequestContextManager:
    """
    Allows overriding options for TestingRequestContextManager.
    """
    return TestingRequestContextManager()


@pytest_asyncio.fixture
async def request_ctx(
    request_ctx_manager: TestingRequestContextManager,
) -> AsyncGenerator[TestingRequestContextManager]:
    """
    Wrap the test function in a request context.

    Fixture value is set to a TestingRequestContextManager instance,
    which can be used for further inspecting and manipulating the
    session under test.

    To override the context manager's instantiation options, simply
    override the request_ctx_manager fixture in a narrower scope
    (eg. module or class level).
    """

    async with request_ctx_manager:
        yield request_ctx_manager
