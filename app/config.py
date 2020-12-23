import os

from mowaki.config import Config


class AppConfig(Config):
    SECRET_KEY: str
    DATABASE_URL: str = 'postgresql://postgres@localhost:5432'
    REDIS_URL: str = 'redis://localhost:6379'

    TEST_MODE: bool = False
    TEST_DATABASE_URL: str = None


config = AppConfig(os.environ)
