"""Shared Shelly Gen2 response helpers and base templates."""

from __future__ import annotations

import uuid
from typing import Any

from aiohttp import web

DEVICE_PREFIX = "shellypro3em-"

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
    "id": f"{DEVICE_PREFIX}virtual",
    "mac": "000000000000",
    "slot": 1,
    "model": "SPEM-003CEBEU",
    "gen": 2,
    "fw_id": "20241011-114455/1.4.4-g6d2a586",
    "ver": "1.4.4",
    "app": "Pro3EM",
    "auth_en": False,
    "auth_domain": None,
    "profile": "triphase",
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
        "name": "Virtual Pro3EM",
        "blink_mode_selector": "active_energy",
        "phase_selector": "all",
        "monitor_phase_sequence": False,
        "reverse": {"a": False, "b": False, "c": False},
        "ct_type": "120A",
    },
}


def device_mac() -> str:
    """Return a deterministic MAC-style identifier."""
    mac_int = uuid.getnode()
    return f"{mac_int:012X}"


def device_id(mac: str | None = None) -> str:
    """Return a Shelly-style device id for the given MAC."""
    mac_value = mac or device_mac()
    return f"{DEVICE_PREFIX}{mac_value.lower()}"


def local_ip(request: web.Request) -> str | None:
    transport = request.transport
    if transport is None:
        return None
    sockname = transport.get_extra_info("sockname")
    if not sockname:
        return None
    return sockname[0]


def em_status_from_values(values: dict[str, float]) -> dict[str, Any]:
    """Build EM.GetStatus response from merged values."""
    return {
        "id": 0,
        "a_current": values.get("l1_current"),
        "a_voltage": values.get("l1_voltage"),
        "a_pf": values.get("l1_pf"),
        "a_freq": values.get("l1_freq"),
        "a_errors": [],
        "b_current": values.get("l2_current"),
        "b_voltage": values.get("l2_voltage"),
        "b_pf": values.get("l2_pf"),
        "b_freq": values.get("l2_freq"),
        "b_errors": [],
        "c_current": values.get("l3_current"),
        "c_voltage": values.get("l3_voltage"),
        "c_pf": values.get("l3_pf"),
        "c_freq": values.get("l3_freq"),
        "c_errors": [],
        "n_current": values.get("n_current"),
        "n_errors": [],
        "total_current": values.get("total_current"),
        "total_act_power": values.get("total_act_power"),
        "total_aprt_power": values.get("total_aprt_power"),
        "user_calibrated_phase": [],
        "errors": [],
    }
