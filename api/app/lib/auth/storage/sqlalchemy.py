from typing import Callable
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine
from .base import SessionStorage


class SQLAlchemySessionStorage(SessionStorage):
    def __init__(self):
        pass

    def set_engine_factory(self, fn: Callable[[], AsyncEngine]):
        pass

    def define_schema(self, metadata: MetaData):
        pass
