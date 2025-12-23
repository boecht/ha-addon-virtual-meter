"""HTTP RPC emulation (real mode)."""

from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Any
from contextlib import suppress

from aiohttp import web

from .config import Settings
from .consumer import HttpConsumer
from .shelly import (
    MOCK_DEVICE_INFO,
    MOCK_EMDATA_STATUS,
    device_id,
    device_mac,
    em_status_from_values,
)
from .transformer import transform


def _json_paths(settings: Settings) -> dict[str, str | None]:
    return {
        "l1_act_power": settings.l1_act_power_json,
        "l2_act_power": settings.l2_act_power_json,
        "l3_act_power": settings.l3_act_power_json,
    }


def _overrides(settings: Settings) -> dict[str, float | None]:
    return {
        "l1_act_power": settings.l1_act_power_value,
        "l2_act_power": settings.l2_act_power_value,
        "l3_act_power": settings.l3_act_power_value,
    }


def create_app(settings: Settings) -> web.Application:
    """Create aiohttp app and register RPC routes for real mode."""
    app = web.Application()
    consumer = HttpConsumer(
        settings.provider_endpoint,
        settings.poll_interval_ms,
        settings.provider_username,
        settings.provider_password,
    )
    cache: dict[str, float] | None = None

    def _device_mac_value() -> str:
        mac = settings.device_mac or device_mac()
        return mac.replace(":", "").upper()

    def _device_id_value() -> str:
        return device_id(_device_mac_value())

    async def _start_background(app: web.Application) -> None:
        from asyncio import sleep

        await sleep(0)
        app["consumer_task"] = app.loop.create_task(consumer.start())
        logging.getLogger("virtual_meter.provider").info("Consumer task started")

    async def _cleanup(app: web.Application) -> None:
        from asyncio import sleep

        await sleep(0)
        task = app.get("consumer_task")
        if task:
            task.cancel()
            with suppress(Exception):
                await task
        await consumer.stop()
        logging.getLogger("virtual_meter.provider").info("Cleanup complete")

    app.on_startup.append(_start_background)
    app.on_cleanup.append(_cleanup)

    async def _on_prepare(request: web.Request, response: web.StreamResponse) -> None:
        from asyncio import sleep

        await sleep(0)
        if "Server" not in response.headers:
            response.headers["Server"] = "ShellyHTTP/1.0.0"

    app.on_response_prepare.append(_on_prepare)

    async def _compute_values() -> dict[str, float]:
        from asyncio import sleep

        await sleep(0)
        nonlocal cache
        latest = consumer.get_latest()
        source_json = latest.data if latest else {}
        values = transform(
            source_json,
            _json_paths(settings),
            _overrides(settings),
        )
        if values:
            cache = values
            return values
        logging.getLogger("virtual_meter.provider").warning(
            "Using cached values; no data available"
        )
        return cache or {}

    async def _status_payload() -> dict[str, Any]:
        values = await _compute_values()
        em_status = em_status_from_values(values)
        sys_status = {
            "mac": _device_mac_value(),
            "time": datetime.now().strftime("%H:%M"),
            "unixtime": int(datetime.now().timestamp()),
        }
        return {
            "sys": sys_status,
            "em:0": em_status,
            "emdata:0": dict(MOCK_EMDATA_STATUS),
        }

    def _device_info_payload() -> dict[str, Any]:
        info = dict(MOCK_DEVICE_INFO)
        mac = _device_mac_value()
        info["mac"] = mac
        info["id"] = device_id(mac)
        info.pop("slot", None)
        info.pop("profile", None)
        return info

    def _emdata_status_payload() -> dict[str, Any]:
        return {"id": 0}

    def _jsonrpc_response(
        request_id: Any,
        result: dict[str, Any] | None,
        error: dict[str, Any] | None = None,
    ) -> web.Response:
        response: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id if request_id is not None else 1,
            "src": _device_id_value(),
        }
        if error is not None:
            response["error"] = error
        else:
            response["result"] = result or {}
        return web.json_response(response)

    async def _rpc_dispatch(method: str) -> dict[str, Any]:
        if method == "Shelly.GetStatus":
            return await _status_payload()
        if method == "Shelly.GetDeviceInfo":
            return _device_info_payload()
        if method == "EM.GetConfig":
            return {
                "id": 0,
                "name": "Virtual Pro3EM",
            }
        if method == "EM.GetStatus":
            return em_status_from_values(await _compute_values())
        if method == "EMData.GetStatus":
            return _emdata_status_payload()
        raise KeyError(method)

    async def _ws_rpc(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        ws.headers["Server"] = "ShellyHTTP/1.0.0"
        await ws.prepare(request)
        logger = logging.getLogger("virtual_meter.requests")
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    body = json.loads(msg.data)
                except json.JSONDecodeError:
                    await ws.send_json(
                        {
                            "id": None,
                            "src": _device_id_value(),
                            "error": {"code": -32700, "message": "Parse error"},
                        }
                    )
                    continue
                method = body.get("method")
                request_id = body.get("id")
                if not method:
                    response = {
                        "id": request_id,
                        "src": _device_id_value(),
                        "error": {"code": -32600, "message": "Invalid Request"},
                    }
                else:
                    try:
                        result = await _rpc_dispatch(method)
                        response = {
                            "id": request_id,
                            "src": _device_id_value(),
                            "result": result,
                        }
                    except KeyError:
                        response = {
                            "id": request_id,
                            "src": _device_id_value(),
                            "error": {"code": -32601, "message": "Method not found"},
                        }
                if settings.debug_logging:
                    logger.debug(
                        json.dumps({"ws_in": msg.data, "ws_out": response}, sort_keys=True)
                    )
                await ws.send_json(response)
            elif msg.type == web.WSMsgType.ERROR:
                logger.warning("WebSocket error: %s", ws.exception())
        return ws

    async def rpc_root(request: web.Request) -> web.StreamResponse:
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
            try:
                result = await _rpc_dispatch(method)
                return _jsonrpc_response(None, result)
            except KeyError:
                return _jsonrpc_response(
                    None, None, {"code": -32601, "message": "Method not found"}
                )

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
        try:
            result = await _rpc_dispatch(method)
            return _jsonrpc_response(request_id, result)
        except KeyError:
            return _jsonrpc_response(
                request_id, None, {"code": -32601, "message": "Method not found"}
            )

    @web.middleware
    async def log_requests(request: web.Request, handler):
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
        logger = logging.getLogger("virtual_meter.requests")
        if settings.debug_logging:
            payload["headers"] = dict(request.headers)
            payload["response_headers"] = dict(response.headers)
            logger.debug(json.dumps(payload, sort_keys=True))
        elif response.status >= 400:
            logger.warning(json.dumps(payload, sort_keys=True))
        return response

    app.middlewares.append(log_requests)

    app.router.add_get("/rpc", rpc_root)
    app.router.add_post("/rpc", rpc_root)

    return app
