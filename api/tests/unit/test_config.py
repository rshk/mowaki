"""
Test configuration loading machinery
"""

from pydantic import AnyUrl, HttpUrl, PostgresDsn
import pytest
from app.config import get_config_from_env


def test_load_minimal_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@database/dbname")
    monkeypatch.delenv("SMTP_URL", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "https://www.example.com")
    monkeypatch.setenv(
        "CORS_ORIGINS", "https://www.example.com https://www2.example.com"
    )

    config = get_config_from_env()
    assert config.database_url == PostgresDsn("postgres://user:pass@database/dbname")
    assert config.smtp_url == AnyUrl("dummy://")
    assert config.frontend_url == HttpUrl("https://www.example.com")
    assert config.cors_origins == [
        "https://www.example.com",
        "https://www2.example.com",
    ]


@pytest.fixture()
def dontcare_defaults(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@database/dbname")
    monkeypatch.delenv("SMTP_URL", raising=False)
    monkeypatch.setenv("FRONTEND_URL", "https://www.example.com")
    monkeypatch.setenv(
        "CORS_ORIGINS", "https://www.example.com https://www2.example.com"
    )


@pytest.mark.usefixtures("dontcare_defaults")
def test_auth_relying_party_id_is_set_automatically_from_domain(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FRONTEND_URL", "https://www.example.com")

    config = get_config_from_env()
    assert config.auth_relying_party_id == "example.com"


@pytest.mark.usefixtures("dontcare_defaults")
def test_auth_relying_party_id_can_be_set_manually(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FRONTEND_URL", "https://www.example.com")
    monkeypatch.setenv("AUTH_RELYING_PARTY_ID", "rp.example.com")

    config = get_config_from_env()
    assert config.auth_relying_party_id == "rp.example.com"
