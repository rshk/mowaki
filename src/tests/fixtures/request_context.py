from collections.abc import AsyncGenerator, Callable

import pytest
import pytest_asyncio

from app.core.context import RequestContext
from tests.utils.session import TestingRequestContextManager


@pytest.fixture
def request_ctx_factory() -> Callable[..., TestingRequestContextManager]:
    def factory():
        # Allows passing arguments into the context manager
        return TestingRequestContextManager()

    return factory


@pytest_asyncio.fixture
async def request_ctx(
    request_ctx_factory: Callable[..., TestingRequestContextManager],
) -> AsyncGenerator[RequestContext]:
    request_ctx_manager = request_ctx_factory()
    async with request_ctx_manager as ctx:
        yield ctx
