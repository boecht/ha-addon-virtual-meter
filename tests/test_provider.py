from __future__ import annotations

import asyncio
import json

from aiohttp.test_utils import TestClient, TestServer

from app import cache
from app.config import Settings
from app.provider import create_app
from app.serializer import encode


def test_shelly_endpoint_returns_device_info():
    async def _run() -> None:
        cache._payloads.clear()
        payload = {
            "id": "shellypro3em-abcdef123456",
            "mac": "ABCDEF123456",
            "model": "SPEM-003CEBEU",
        }
        cache.set_payload("Shelly.GetDeviceInfo", encode(payload))
        settings = Settings(provider_endpoint="http://example", poll_interval_ms=1000)
        app = create_app(settings, payload["id"])
        client = TestClient(TestServer(app))
        await client.start_server()
        resp = await client.get("/shelly")
        assert resp.status == 200
        body = await resp.text()
        assert json.loads(body) == payload
        await client.close()

    asyncio.run(_run())


def test_shelly_endpoint_missing_payload_returns_404():
    async def _run() -> None:
        cache._payloads.clear()
        settings = Settings(provider_endpoint="http://example", poll_interval_ms=1000)
        app = create_app(settings, "shellypro3em-abcdef123456")
        client = TestClient(TestServer(app))
        await client.start_server()
        resp = await client.get("/shelly")
        assert resp.status == 404
        body = await resp.text()
        assert body == ""
        await client.close()

    asyncio.run(_run())
