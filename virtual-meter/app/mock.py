"""Mock Shelly Gen2 RPC emulation (full surface for protocol capture)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
import uuid
from typing import Any, Callable

from aiohttp import web

from .config import Settings
from .transformer import em_status_from_values, transform

DEVICE_ID = "shellypro3em-virtual"

MOCK_EM_STATUS = {
    "id": 0,
    "a_current": 0.0,
    "a_voltage": 0.0,
    "a_act_power": 0.0,
    "a_aprt_power": 0.0,
    "a_pf": 0.0,
    "a_freq": 0.0,
    "a_errors": [],
    "b_current": 0.0,
    "b_voltage": 0.0,
    "b_act_power": 0.0,
    "b_aprt_power": 0.0,
    "b_pf": 0.0,
    "b_freq": 0.0,
    "b_errors": [],
    "c_current": 0.0,
    "c_voltage": 0.0,
    "c_act_power": 0.0,
    "c_aprt_power": 0.0,
    "c_pf": 0.0,
    "c_freq": 0.0,
    "c_errors": [],
    "n_current": 0.0,
    "n_errors": [],
    "total_current": 0.0,
    "total_act_power": 0.0,
    "total_aprt_power": 0.0,
    "user_calibrated_phase": [],
    "errors": [],
}

MOCK_EMDATA_STATUS = {
    "id": 0,
    "a_total_act_energy": 0.0,
    "a_total_act_ret_energy": 0.0,
    "b_total_act_energy": 0.0,
    "b_total_act_ret_energy": 0.0,
    "c_total_act_energy": 0.0,
    "c_total_act_ret_energy": 0.0,
    "total_act": 0.0,
    "total_act_ret": 0.0,
    "errors": [],
}

MOCK_DEVICE_INFO = {
    "id": DEVICE_ID,
    "mac": "000000000000",
    "model": "SPEM-003CEBEU",
    "gen": 2,
    "fw_id": "20241011-114455/1.4.4-g6d2a586",
    "ver": "1.4.4",
    "app": "Pro3EM",
    "auth_en": False,
    "auth_domain": None,
}

MOCK_SHELLY_STATUS = {
    "sys": {
        "mac": MOCK_DEVICE_INFO["mac"],
        "uptime": 123,
        "ram_size": 256000,
        "ram_free": 120000,
        "fs_size": 800000,
        "fs_free": 400000,
        "cfg_rev": 1,
        "kvs_rev": 1,
        "schedule_rev": 0,
        "webhook_rev": 0,
        "restart_required": False,
        "time": "12:00",
        "unixtime": 1734825600,
        "available_updates": {},
    },
    "wifi": {
        "sta_ip": None,
        "status": "disconnected",
        "ssid": None,
        "rssi": 0,
    },
    "eth": {
        "ip": None,
    },
    "ble": {},
    "cloud": {"connected": False},
    "mqtt": {"connected": False},
    "ws": {"connected": False},
    "modbus": {"enabled": False},
    "bthome": {"errors": ["bluetooth_disabled"]},
    "script:0": {"id": 0, "running": False},
    "em:0": MOCK_EM_STATUS,
    "emdata:0": MOCK_EMDATA_STATUS,
}

MOCK_SHELLY_CONFIG = {
    "sys": {
        "device": {
            "name": "Virtual Pro 3EM",
            "eco_mode": False,
            "mac": MOCK_DEVICE_INFO["mac"],
            "fw_id": MOCK_DEVICE_INFO["fw_id"],
            "discoverable": True,
            "addon_type": None,
        },
        "websocket": {"enable": False},
        "udp": {"addr": None},
        "ui_data": {},
        "rpc_udp": {"dst_addr": None, "listen_port": None},
        "sntp": {"server": "time.google.com"},
        "cfg_rev": 1,
    },
    "wifi": {
        "ap": {
            "ssid": None,
            "is_open": True,
            "enable": False,
            "range_extender": {"enable": False},
        },
        "sta": {
            "ssid": None,
            "is_open": True,
            "enable": False,
            "ipv4mode": "dhcp",
            "ip": None,
            "netmask": None,
            "gw": None,
            "nameserver": None,
        },
        "sta1": {
            "ssid": None,
            "is_open": True,
            "enable": False,
            "ipv4mode": "dhcp",
            "ip": None,
            "netmask": None,
            "gw": None,
            "nameserver": None,
        },
        "roam": {"rssi_thr": -80, "interval": 60},
    },
    "eth": {
        "enable": True,
        "ipv4mode": "dhcp",
        "ip": None,
        "netmask": None,
        "gw": None,
        "nameserver": None,
    },
    "ble": {"enable": False, "rpc": {"enable": False}, "observer": {"enable": False}},
    "cloud": {"enable": False, "server": None},
    "mqtt": {"enable": False},
    "ws": {"enable": False, "server": None, "ssl_ca": "ca.pem"},
    "modbus": {"enable": False},
    "bthome": {},
    "script:0": {"id": 0, "name": "script_0", "enable": False},
    "em:0": {
        "id": 0,
        "name": "Grid",
        "blink_mode_selector": "active_energy",
        "phase_selector": "all",
        "monitor_phase_sequence": False,
        "reverse": {"a": False, "b": False, "c": False},
        "ct_type": "120A",
    },
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _device_mac() -> str:
    mac_int = uuid.getnode()
    return f"{mac_int:012X}"


def _log_request(request: web.Request, rpc_method: str | None, status: int) -> None:
    payload = {
        "ts": _timestamp(),
        "method": request.method,
        "path": request.path,
        "query": request.query_string,
        "rpc_method": rpc_method,
        "remote": request.remote,
        "status": status,
        "headers": {
            "user-agent": request.headers.get("User-Agent"),
            "accept": request.headers.get("Accept"),
            "content-type": request.headers.get("Content-Type"),
        },
    }
    logging.getLogger("virtual_meter.requests").info(json.dumps(payload, sort_keys=True))


def _rpc_response(
    request: web.Request,
    result: dict[str, Any] | None,
    error: dict[str, Any] | None = None,
) -> web.Response:
    request_id = request.query.get("id")
    response: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": request_id or 1,
        "src": DEVICE_ID,
        "dst": request.query.get("src") or "client",
    }
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result or {}
    return web.json_response(response)


def _rpc_response_from_body(body: dict[str, Any], result: dict[str, Any] | None, error: dict[str, Any] | None) -> web.Response:
    response: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": body.get("id", 1),
        "src": DEVICE_ID,
        "dst": body.get("src") or "client",
    }
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result or {}
    return web.json_response(response)


def _result_only_response(result: dict[str, Any] | None, error: dict[str, Any] | None = None) -> web.Response:
    if error is not None:
        return web.json_response({"error": error})
    return web.json_response({"result": result or {}})


def _build_components(status_map: dict[str, Any], include: set[str] | None = None) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    config_map = dict(MOCK_SHELLY_CONFIG)
    for key in sorted(set(status_map) | set(config_map)):
        entry: dict[str, Any] = {"key": key}
        if include is None or "status" in include:
            entry["status"] = status_map.get(key)
        if include is None or "config" in include:
            entry["config"] = config_map.get(key)
        components.append(entry)
    return components


def _local_ip(request: web.Request) -> str | None:
    transport = request.transport
    if transport is None:
        return None
    sockname = transport.get_extra_info("sockname")
    if not sockname:
        return None
    return sockname[0]


def _build_status(request: web.Request) -> dict[str, Any]:
    status = dict(MOCK_SHELLY_STATUS)
    mac = _device_mac()
    now = datetime.now()

    sys_status = dict(status["sys"])
    sys_status["mac"] = mac
    sys_status["time"] = now.strftime("%H:%M")
    sys_status["unixtime"] = int(now.timestamp())
    status["sys"] = sys_status

    eth_status = dict(status["eth"])
    eth_status["ip"] = _local_ip(request)
    status["eth"] = eth_status
    return status


def _override_map(settings: Settings) -> dict[str, float | None]:
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
        "n_current": settings.n_current_value,
        "total_current": settings.total_current_value,
        "total_act_power": settings.total_act_power_value,
        "total_aprt_power": settings.total_aprt_power_value,
    }


def _mock_em_status(settings: Settings) -> dict[str, Any]:
    values = transform({}, {}, _override_map(settings), settings.defaults, derive=False)
    return em_status_from_values(values)


def _mock_methods(settings: Settings) -> dict[str, Callable[[web.Request, dict[str, Any] | None], dict[str, Any]]]:
    return {
        "Shelly.GetStatus": lambda r, _p: {**_build_status(r), "em:0": _mock_em_status(settings)},
        "Shelly.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG,
        "Shelly.ListMethods": lambda _r, _p: {"methods": sorted(_mock_methods(settings).keys())},
        "Shelly.GetDeviceInfo": lambda _r, _p: MOCK_DEVICE_INFO,
        "Shelly.GetComponents": lambda r, params: {
            "cfg_rev": 1,
            "offset": 0,
            "total": len(MOCK_SHELLY_STATUS),
            "components": _build_components(
                {**_build_status(r), "em:0": _mock_em_status(settings)},
                set((params or {}).get("include", [])) if (params or {}).get("include") else None
            ),
        },
        "EM.GetStatus": lambda _r, _p: _mock_em_status(settings),
        "EM.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG["em:0"],
        "EMData.GetStatus": lambda _r, _p: MOCK_EMDATA_STATUS,
        "EMData.GetConfig": lambda _r, _p: {},
        "EMData.GetRecords": lambda _r, _p: {"records": []},
        "EMData.GetData": lambda _r, _p: {"keys": [], "data": []},
        "EMData.GetNetEnergies": lambda _r, _p: {"total_act": 0.0, "total_act_ret": 0.0},
        "EMData.ResetCounters": lambda _r, _p: {"restart_required": False},
        "EMData.DeleteAllData": lambda _r, _p: {"restart_required": False},
        "EM1Data.GetStatus": lambda _r, _p: {"id": 0, "total_act_energy": 0.0, "total_act_ret_energy": 0.0, "errors": []},
        "EM1Data.GetConfig": lambda _r, _p: {},
        "EM1Data.GetRecords": lambda _r, _p: {"records": []},
        "EM1Data.GetData": lambda _r, _p: {"keys": [], "data": []},
        "EM1Data.GetNetEnergies": lambda _r, _p: {"total_act": 0.0, "total_act_ret": 0.0},
        "EM1Data.ResetCounters": lambda _r, _p: {"restart_required": False},
        "EM1Data.DeleteAllData": lambda _r, _p: {"restart_required": False},
        "System.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("sys", {}),
        "System.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("sys", {}),
        "WiFi.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("wifi", {}),
        "WiFi.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("wifi", {}),
        "Ethernet.GetStatus": lambda r, _p: _build_status(r).get("eth", {}),
        "Ethernet.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("eth", {}),
        "Cloud.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("cloud", {}),
        "Cloud.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("cloud", {}),
        "MQTT.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("mqtt", {}),
        "MQTT.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("mqtt", {}),
        "WS.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("ws", {}),
        "WS.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("ws", {}),
        "Modbus.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("modbus", {}),
        "Modbus.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("modbus", {}),
        "BLE.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("ble", {}),
        "BLE.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("ble", {}),
        "BTHome.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("bthome", {}),
        "BTHome.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("bthome", {}),
        "Script.GetStatus": lambda _r, _p: MOCK_SHELLY_STATUS.get("script:0", {}),
        "Script.GetConfig": lambda _r, _p: MOCK_SHELLY_CONFIG.get("script:0", {}),
    }


def _get_mock_result(method: str, request: web.Request, params: dict[str, Any] | None) -> dict[str, Any] | None:
    methods = _mock_methods(request.app["settings"])
    handler = methods.get(method)
    if handler is None:
        return None
    return handler(request, params)


def _extract_params_from_query(query: dict[str, str]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key, value in query.items():
        if key in {"id", "src"}:
            continue
        params[key] = value
    return params


def _mock_middleware(settings: Settings):
    @web.middleware
    async def middleware(request: web.Request, handler):
        try:
            response = await handler(request)
        except Exception as exc:
            logging.getLogger("virtual_meter.requests").exception("Request failed")
            raise exc
        if settings.mock_mode:
            rpc_method = request.match_info.get("method")
            _log_request(request, rpc_method, response.status)
        return response

    return middleware


def create_app(settings: Settings) -> web.Application:
    """Create aiohttp app and register RPC routes (mock mode only)."""
    app = web.Application(middlewares=[_mock_middleware(settings)])
    app["settings"] = settings
    logging.getLogger("virtual_meter.mock").info("Mock API initialized")

    async def shelly_get_status(request: web.Request) -> web.Response:
        from asyncio import sleep
        await sleep(0)
        return web.json_response({**_build_status(request), "em:0": _mock_em_status(settings)})

    async def em_get_status(request: web.Request) -> web.Response:
        from asyncio import sleep
        await sleep(0)
        return web.json_response(_mock_em_status(settings))

    async def shelly_device_info(request: web.Request) -> web.Response:
        from asyncio import sleep
        await sleep(0)
        info = dict(MOCK_DEVICE_INFO)
        info["mac"] = _device_mac()
        return web.json_response(info)

    async def rpc_root(request: web.Request) -> web.Response:
        try:
            body = await request.json()
        except Exception:
            body = {}
        method = body.get("method")
        params = body.get("params") or {}
        result = _get_mock_result(method, request, params) if method else None
        if result is None:
            error = {"code": -32601, "message": "Method not found"}
            response = _rpc_response_from_body(body, None, error)
        else:
            response = _rpc_response_from_body(body, result, None)
        return response

    async def rpc_method(request: web.Request) -> web.Response:
        method = request.match_info["method"]
        params = _extract_params_from_query(dict(request.query))
        if request.can_read_body:
            try:
                body = await request.json()
                if isinstance(body, dict) and body.get("params"):
                    params = body.get("params")
            except Exception:
                pass
        result = _get_mock_result(method, request, params)
        if result is None:
            return _result_only_response(None, {"code": -32601, "message": "Method not found"})
        return _result_only_response(result)

    app.router.add_get("/shelly", shelly_device_info)
    app.router.add_get("/rpc/Shelly.GetStatus", shelly_get_status)
    app.router.add_get("/rpc/EM.GetStatus", em_get_status)
    app.router.add_route("*", "/rpc", rpc_root)
    app.router.add_route("*", "/rpc/{method}", rpc_method)

    return app
