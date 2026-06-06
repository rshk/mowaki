"""
Test configuration loading machinery
"""

from pydantic import HttpUrl, PostgresDsn
import pytest
from app.config import get_config_from_env


def test_load_minimal_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@database/dbname")
    monkeypatch.delenv("SMTP_URL", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "https://www.example.com")
    monkeypatch.setenv("CORS_ORIGINS", "https://www.example.com https://www2.example.com")

    config = get_config_from_env()
    assert config.database_url == PostgresDsn("postgres://user:pass@database/dbname")
    assert config.smtp_url == "dummy://"
    assert config.frontend_url == HttpUrl("https://www.example.com")
    assert config.cors_origins == [
        "https://www.example.com",
        "https://www2.example.com",
    ]
