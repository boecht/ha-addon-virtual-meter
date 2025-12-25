"""Poll the upstream HTTP endpoint and emit raw payload snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

from aiohttp import ClientSession, ClientTimeout
import logging


@dataclass
class ConsumerSnapshot:
    """Raw payload snapshot returned by the poller."""

    raw: bytes
    fetched_at: datetime


class HttpConsumer:
    """Poll an HTTP endpoint on a fixed interval and track the latest snapshot."""

    def __init__(
        self,
        endpoint: str,
        poll_interval_ms: int,
        username: str | None,
        password: str | None,
    ) -> None:
        self.endpoint = endpoint
        self.poll_interval_ms = poll_interval_ms
        self.username = username
        self.password = password
        self.latest: ConsumerSnapshot | None = None
        self._session: ClientSession | None = None

    async def start(
        self, on_update: Callable[[ConsumerSnapshot], Awaitable[None]] | None = None
    ) -> None:
        """Start the polling loop and invoke the optional update callback."""
        logger = logging.getLogger("virtual_meter.poller")
        timeout = ClientTimeout(total=10)
        self._session = ClientSession(timeout=timeout)
        logger.info(
            "Poller started (endpoint=%s, interval_ms=%s)",
            self.endpoint,
            self.poll_interval_ms,
        )
        try:
            while True:
                try:
                    params = None
                    if self.username and self.password:
                        params = {"user": self.username, "password": self.password}
                    async with self._session.get(self.endpoint, params=params) as resp:
                        raw = await resp.read()
                        snapshot = ConsumerSnapshot(
                            raw=raw, fetched_at=datetime.now(timezone.utc)
                        )
                        self.latest = snapshot
                        if on_update is not None:
                            await on_update(snapshot)
                except Exception:
                    logger.exception("Failed to fetch provider endpoint")
                    # Keep last known good data
                await _sleep_ms(self.poll_interval_ms)
        finally:
            await self._close_session()

    def get_latest(self) -> ConsumerSnapshot | None:
        """Return the most recent snapshot (if any)."""
        return self.latest

    async def stop(self) -> None:
        """Stop the poller and close any open HTTP session."""
        await self._close_session()

    async def _close_session(self) -> None:
        """Close the HTTP session if it is open."""
        if self._session is not None and not self._session.closed:
            await self._session.close()


async def _sleep_ms(duration_ms: int) -> None:
    """Async sleep helper using milliseconds."""
    from asyncio import sleep

    await sleep(duration_ms / 1000.0)
