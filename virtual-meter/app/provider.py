"""HTTP RPC emulation (real mode)."""

from __future__ import annotations

from datetime import datetime

from aiohttp import web

from .config import Settings
from .consumer import HttpConsumer
from .mock import MOCK_SHELLY_STATUS, _device_mac, _local_ip
from .transformer import em_status_from_values, transform


def _json_paths(settings: Settings) -> dict[str, str | None]:
    return {
        "l1_current": settings.l1_current_json,
        "l1_voltage": settings.l1_voltage_json,
        "l1_act_power": settings.l1_act_power_json,
        "l1_aprt_power": settings.l1_aprt_power_json,
        "l1_pf": settings.l1_pf_json,
        "l1_freq": settings.l1_freq_json,
        "l2_current": settings.l2_current_json,
        "l2_voltage": settings.l2_voltage_json,
        "l2_act_power": settings.l2_act_power_json,
        "l2_aprt_power": settings.l2_aprt_power_json,
        "l2_pf": settings.l2_pf_json,
        "l2_freq": settings.l2_freq_json,
        "l3_current": settings.l3_current_json,
        "l3_voltage": settings.l3_voltage_json,
        "l3_act_power": settings.l3_act_power_json,
        "l3_aprt_power": settings.l3_aprt_power_json,
        "l3_pf": settings.l3_pf_json,
        "l3_freq": settings.l3_freq_json,
        "total_current": settings.total_current_json,
        "total_act_power": settings.total_act_power_json,
        "total_aprt_power": settings.total_aprt_power_json,
    }


def _overrides(settings: Settings) -> dict[str, float | None]:
    return {
        "l1_current": settings.l1_current_value,
        "l1_voltage": settings.l1_voltage_value,
        "l1_act_power": settings.l1_act_power_value,
        "l1_aprt_power": settings.l1_aprt_power_value,
        "l1_pf": settings.l1_pf_value,
        "l1_freq": settings.l1_freq_value,
        "l2_current": settings.l2_current_value,
        "l2_voltage": settings.l2_voltage_value,
        "l2_act_power": settings.l2_act_power_value,
        "l2_aprt_power": settings.l2_aprt_power_value,
        "l2_pf": settings.l2_pf_value,
        "l2_freq": settings.l2_freq_value,
        "l3_current": settings.l3_current_value,
        "l3_voltage": settings.l3_voltage_value,
        "l3_act_power": settings.l3_act_power_value,
        "l3_aprt_power": settings.l3_aprt_power_value,
        "l3_pf": settings.l3_pf_value,
        "l3_freq": settings.l3_freq_value,
        "total_current": settings.total_current_value,
        "total_act_power": settings.total_act_power_value,
        "total_aprt_power": settings.total_aprt_power_value,
    }


def create_app(settings: Settings) -> web.Application:
    """Create aiohttp app and register RPC routes for real mode."""
    app = web.Application()
    consumer = HttpConsumer(settings.provider_endpoint, settings.poll_interval_ms)
    cache: dict[str, float] | None = None

    async def _start_background(app: web.Application) -> None:
        from asyncio import sleep
        await sleep(0)
        app["consumer_task"] = app.loop.create_task(consumer.start())

    async def _cleanup(app: web.Application) -> None:
        from asyncio import sleep
        await sleep(0)
        task = app.get("consumer_task")
        if task:
            task.cancel()

    app.on_startup.append(_start_background)
    app.on_cleanup.append(_cleanup)

    async def _compute_values() -> dict[str, float]:
        from asyncio import sleep
        await sleep(0)
        nonlocal cache
        latest = consumer.get_latest()
        source_json = latest.data if latest else {}
        values = transform(source_json, _json_paths(settings), _overrides(settings), settings.defaults, derive=True)
        if values:
            cache = values
            return values
        return cache or {}

    async def shelly_get_status(request: web.Request) -> web.Response:
        values = await _compute_values()
        em_status = em_status_from_values(values)
        status = dict(MOCK_SHELLY_STATUS)
        sys_status = dict(status["sys"])
        sys_status["mac"] = _device_mac()
        sys_status["time"] = datetime.now().strftime("%H:%M")
        sys_status["unixtime"] = int(datetime.now().timestamp())
        status["sys"] = sys_status

        eth_status = dict(status["eth"])
        eth_status["ip"] = _local_ip(request)
        status["eth"] = eth_status

        status["em:0"] = em_status
        status["emdata:0"] = {"id": 0}
        return web.json_response(status)

    async def em_get_status(request: web.Request) -> web.Response:
        values = await _compute_values()
        return web.json_response(em_status_from_values(values))

    app.router.add_get("/rpc/Shelly.GetStatus", shelly_get_status)
    app.router.add_get("/rpc/EM.GetStatus", em_get_status)

    return app
