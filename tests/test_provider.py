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


def test_rpc_post_malformed_body_returns_jsonrpc_errors():
    async def _run() -> None:
        cache._payloads.clear()
        settings = Settings(provider_endpoint="http://example", poll_interval_ms=1000)
        app = create_app(settings, "shellypro3em-abcdef123456")
        client = TestClient(TestServer(app))
        await client.start_server()
        resp = await client.post("/rpc", data=b"not json")
        assert resp.status == 400
        assert json.loads(await resp.text())["error"]["code"] == -32700
        resp = await client.post("/rpc", data=b"[1]")
        assert resp.status == 400
        assert json.loads(await resp.text())["error"]["code"] == -32600
        await client.close()

    asyncio.run(_run())


def test_rpc_websocket_non_object_keeps_connection_open():
    async def _run() -> None:
        cache._payloads.clear()
        payload = {"id": "shellypro3em-abcdef123456", "mac": "ABCDEF123456"}
        cache.set_payload("Shelly.GetDeviceInfo", encode(payload))
        settings = Settings(provider_endpoint="http://example", poll_interval_ms=1000)
        app = create_app(settings, payload["id"])
        client = TestClient(TestServer(app))
        await client.start_server()
        ws = await client.ws_connect("/rpc")
        await ws.send_str("[1]")
        assert json.loads(await ws.receive_bytes())["error"]["code"] == -32600
        await ws.send_str(json.dumps({"id": 2, "method": "Shelly.GetDeviceInfo"}))
        assert json.loads(await ws.receive_bytes())["result"] == payload
        await ws.close()
        await client.close()

    asyncio.run(_run())
