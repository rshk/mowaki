import asyncio
from typing import AsyncIterator

import strawberry

# from app.io.db import get_redis_connection


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> AsyncIterator[int]:
        for i in range(target):
            yield i
            await asyncio.sleep(1)

    # TODO: demo something getting stuff from redis pub/sub

    # @strawberry.subscription
    # async def boop(self) -> AsyncIterator[str]:
    #     rc = get_redis_connection()
    #     ps = rc.pubsub()
    #     await ps.subscribe("boop")
    #     # ignore_subscribe_messages=True
    #     async for msg in ps.listen():
    #         if msg["type"] == "message":
    #             yield msg["data"].decode()
