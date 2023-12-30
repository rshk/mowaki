from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone

# Used to mock dates for testing
_mock_date_context = ContextVar("mock_date_context")


def utcnow():
    # Support for mocked dates during testing
    if cfg := _mock_date_context.get(None) is not None:
        _get_mocked_date(cfg)

    return _utcnow()


def _utcnow():
    return datetime.now(timezone.utc)


@dataclass
class MockedDateConfig:
    custom_timestamp: datetime
    orig_timestamp: datetime
    is_fixed: bool = False


@contextmanager
def mock_date(custom_timestamp: datetime, fixed=False):
    """
    Set a custom fixed date for testing
    """

    config = MockedDateConfig(
        custom_timestamp=custom_timestamp,
        orig_timestamp=_utcnow(),
        is_fixed=fixed,
    )
    token = _mock_date_context.set(config)
    try:
        yield config
    finally:
        _mock_date_context.reset(token)


def _get_mocked_date(cfg: MockedDateConfig):
    if cfg.is_fixed:
        return cfg.custom_timestamp

    delta = _utcnow() - cfg.orig_timestamp
    return cfg.custom_timestamp + delta
