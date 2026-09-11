from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, Response

from app.const import SESSION_TOKEN_HEADER
from app.svc.webapi.app import create_app


class AsyncTestClient(AsyncClient):
    """
    Custom FastAPI test client, using async
    """

    async def request(self, *args, **kwargs) -> Response:
        response = await super().request(*args, **kwargs)

        # Set Bearer token from response as needed
        if (new_token := response.headers.get(SESSION_TOKEN_HEADER)) is not None:
            self.headers["Authorization"] = f"Bearer {new_token}"

        return response


@pytest_asyncio.fixture()
async def testclient(database_schema) -> AsyncGenerator[AsyncClient]:
    app = create_app()
    client = AsyncTestClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )
    async with client as tc:
        yield tc
