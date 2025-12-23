"""Shared Shelly Gen2 response helpers and base templates."""

from __future__ import annotations

import uuid
from typing import Any

DEVICE_PREFIX = "shellypro3em-"

MOCK_EMDATA_STATUS = {
    "id": 0,
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



def device_mac() -> str:
    """Return a deterministic MAC-style identifier."""
    mac_int = uuid.getnode()
    return f"{mac_int:012X}"


def device_id(mac: str | None = None) -> str:
    """Return a Shelly-style device id for the given MAC."""
    mac_value = mac or device_mac()
    return f"{DEVICE_PREFIX}{mac_value.lower()}"


def em_status_from_values(values: dict[str, float]) -> dict[str, Any]:
    """Build EM.GetStatus response from merged values."""
    return {
        "id": 0,
        "a_act_power": values.get("l1_act_power"),
        "b_act_power": values.get("l2_act_power"),
        "c_act_power": values.get("l3_act_power"),
    }
