from __future__ import annotations

import asyncio
import logging

import pytest

from app import consumer
from app.consumer import HttpConsumer


def test_consumer_logs_timeout_as_warning(caplog, monkeypatch):
    event = asyncio.Event()

    class FakeResponse:
        async def __aenter__(self):
            event.set()
            raise asyncio.TimeoutError()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        closed = False

        def __init__(self, timeout=None):
            self.timeout = timeout

        def get(self, *args, **kwargs):
            return FakeResponse()

        async def close(self):
            await asyncio.sleep(0)
            self.closed = True

    async def fake_sleep_ms(_duration_ms: int) -> None:
        raise asyncio.CancelledError()

    monkeypatch.setattr(consumer, "ClientSession", lambda timeout=None: FakeSession())
    monkeypatch.setattr(consumer, "_sleep_ms", fake_sleep_ms)

    async def _run() -> None:
        hc = HttpConsumer("http://example", 1000, None, None)
        with caplog.at_level(logging.WARNING, logger="virtual_meter.poller"):
            task = asyncio.create_task(hc.start())
            await event.wait()
            await task

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(_run())

    assert "Failed to fetch provider endpoint (10s timeout)" in caplog.text
