"""Universal HTTP source consumer for grid data sources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aiohttp import ClientSession, ClientTimeout
import logging


@dataclass
class ConsumerSnapshot:
    data: dict[str, Any]
    fetched_at: datetime


class HttpConsumer:
    def __init__(self, endpoint: str, poll_interval_ms: int) -> None:
        self.endpoint = endpoint
        self.poll_interval_ms = poll_interval_ms
        self.latest: ConsumerSnapshot | None = None
        self._session: ClientSession | None = None

    async def start(self) -> None:
        """Start background polling."""
        logger = logging.getLogger("virtual_meter.consumer")
        timeout = ClientTimeout(total=10)
        self._session = ClientSession(timeout=timeout)
        while True:
            try:
                async with self._session.get(self.endpoint) as resp:
                    payload = await resp.json(content_type=None)
                    if isinstance(payload, dict):
                        self.latest = ConsumerSnapshot(data=payload, fetched_at=datetime.now(timezone.utc))
            except Exception:
                logger.exception("Failed to fetch provider endpoint")
                # Keep last known good data
                pass
            await _sleep_ms(self.poll_interval_ms)

    def get_latest(self) -> ConsumerSnapshot | None:
        return self.latest


async def _sleep_ms(duration_ms: int) -> None:
    from asyncio import sleep

    await sleep(duration_ms / 1000.0)
