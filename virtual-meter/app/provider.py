"""Serve cached RPC payloads over HTTP/WebSocket with JSON-RPC framing."""

from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Any

from aiohttp import web

from .cache import get_payload
from .config import Settings


def create_app(settings: Settings, device_id: str) -> web.Application:
    """Create the aiohttp app that serves cached payloads."""
    app = web.Application()
    rpc_logger = logging.getLogger("virtual_meter.rpc")
    request_logger = logging.getLogger("virtual_meter.rpc.requests")

    async def _on_prepare(request: web.Request, response: web.StreamResponse) -> None:
        """Inject the emulated server header when missing."""
        from asyncio import sleep

        await sleep(0)
        if "Server" not in response.headers:
            response.headers["Server"] = "ShellyHTTP/1.0.0"

    app.on_response_prepare.append(_on_prepare)

    def _jsonrpc_success_bytes(request_id: Any, result_bytes: bytes) -> bytes:
        """Wrap an already-serialized result in a JSON-RPC success envelope."""
        request_id_value = request_id if request_id is not None else 1
        id_json = json.dumps(request_id_value, separators=(",", ":"), sort_keys=True)
        src_json = json.dumps(device_id, separators=(",", ":"), sort_keys=True)
        if not isinstance(result_bytes, (bytes, bytearray)):
            result_bytes = str(result_bytes).encode("utf-8")
        return (
            b'{"jsonrpc":"2.0","id":'
            + id_json.encode("utf-8")
            + b',"src":'
            + src_json.encode("utf-8")
            + b',"result":'
            + bytes(result_bytes)
            + b"}"
        )

    def _jsonrpc_error_bytes(request_id: Any, error: dict[str, Any]) -> bytes:
        """Build a JSON-RPC error envelope."""
        request_id_value = request_id if request_id is not None else 1
        id_json = json.dumps(request_id_value, separators=(",", ":"), sort_keys=True)
        src_json = json.dumps(device_id, separators=(",", ":"), sort_keys=True)
        error_json = json.dumps(error, separators=(",", ":"), sort_keys=True)
        return (
            b'{"jsonrpc":"2.0","id":'
            + id_json.encode("utf-8")
            + b',"src":'
            + src_json.encode("utf-8")
            + b',"error":'
            + error_json.encode("utf-8")
            + b"}"
        )

    async def _dispatch_payload(method: str) -> bytes | None:
        """Resolve a cached payload for the given RPC method."""
        from asyncio import sleep

        await sleep(0)
        return get_payload(method)

    async def _ws_rpc(request: web.Request) -> web.WebSocketResponse:
        """Handle JSON-RPC over WebSocket."""
        ws = web.WebSocketResponse()
        ws.headers["Server"] = "ShellyHTTP/1.0.0"
        await ws.prepare(request)
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    body = json.loads(msg.data)
                except json.JSONDecodeError:
                    await ws.send_bytes(
                        _jsonrpc_error_bytes(
                            None, {"code": -32700, "message": "Parse error"}
                        )
                    )
                    continue
                method = body.get("method")
                request_id = body.get("id")
                if not method:
                    response_bytes = _jsonrpc_error_bytes(
                        request_id, {"code": -32600, "message": "Invalid Request"}
                    )
                else:
                    payload = await _dispatch_payload(method)
                    if payload is None:
                        response_bytes = _jsonrpc_error_bytes(
                            request_id, {"code": -32601, "message": "Method not found"}
                        )
                    else:
                        response_bytes = _jsonrpc_success_bytes(request_id, payload)
                if settings.debug_logging:
                    rpc_logger.debug(
                        json.dumps(
                            {
                                "ws_in": msg.data,
                                "ws_out": response_bytes.decode("utf-8", "replace"),
                            }
                        )
                    )
                await ws.send_bytes(response_bytes)
            elif msg.type == web.WSMsgType.ERROR:
                rpc_logger.info("WebSocket error: %s", ws.exception())
        return ws

    async def rpc_root(request: web.Request) -> web.StreamResponse:
        """Route JSON-RPC requests over HTTP or WebSocket."""
        ws_probe = web.WebSocketResponse()
        if ws_probe.can_prepare(request):
            return await _ws_rpc(request)
        if request.method == "GET":
            method = request.query.get("method")
            if not method:
                response = web.StreamResponse(
                    status=500,
                    headers={"Server": "ShellyHTTP/1.0.0", "Content-Length": "0"},
                )
                await response.prepare(request)
                await response.write_eof()
                return response
            payload = await _dispatch_payload(method)
            if payload is None:
                response_bytes = _jsonrpc_error_bytes(
                    None, {"code": -32601, "message": "Method not found"}
                )
            else:
                response_bytes = _jsonrpc_success_bytes(None, payload)
            return web.Response(body=response_bytes, content_type="application/json")

        body = await request.json()
        method = body.get("method")
        request_id = body.get("id")
        if not method:
            response = web.StreamResponse(
                status=500,
                headers={"Server": "ShellyHTTP/1.0.0", "Content-Length": "0"},
            )
            await response.prepare(request)
            await response.write_eof()
            return response
        payload = await _dispatch_payload(method)
        if payload is None:
            response_bytes = _jsonrpc_error_bytes(
                request_id, {"code": -32601, "message": "Method not found"}
            )
        else:
            response_bytes = _jsonrpc_success_bytes(request_id, payload)
        return web.Response(body=response_bytes, content_type="application/json")

    async def shelly_info(request: web.Request) -> web.StreamResponse:
        """Return the raw Shelly.GetDeviceInfo payload."""
        payload = await _dispatch_payload("Shelly.GetDeviceInfo")
        if payload is None:
            return web.Response(status=404, body=b"", content_type="application/json")
        return web.Response(body=payload, content_type="application/json")

    @web.middleware
    async def log_requests(request: web.Request, handler):
        """Log request/response metadata, including RPC payloads when present."""
        rpc_payload: dict[str, Any] | None = None
        if request.path.startswith("/rpc"):
            if request.method == "GET":
                method = request.query.get("method")
                rpc_payload = {
                    "transport": "query",
                    "method": method or request.match_info.get("method"),
                    "query": dict(request.query),
                }
            else:
                try:
                    body = await request.json()
                except Exception:
                    body = await request.text()
                rpc_payload = {
                    "transport": "body",
                    "body": body,
                }
        response = await handler(request)
        payload = {
            "ts": datetime.now().isoformat(),
            "method": request.method,
            "path": request.path,
            "query": request.query_string,
            "status": response.status,
            "remote": request.remote,
            "headers": {
                "user-agent": request.headers.get("User-Agent"),
                "accept": request.headers.get("Accept"),
            },
        }
        if rpc_payload is not None:
            payload["rpc"] = rpc_payload
        if settings.debug_logging:
            payload["headers"] = dict(request.headers)
            payload["response_headers"] = dict(response.headers)
            request_logger.debug(json.dumps(payload, sort_keys=True))
        elif response.status >= 400:
            request_logger.warning(json.dumps(payload, sort_keys=True))
        return response

    app.middlewares.append(log_requests)

    app.router.add_get("/rpc", rpc_root)
    app.router.add_post("/rpc", rpc_root)
    app.router.add_get("/shelly", shelly_info)

    return app
