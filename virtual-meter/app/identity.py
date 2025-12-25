"""Device identity helpers for the emulated hardware."""

from __future__ import annotations

import uuid

DEVICE_PREFIX = "shellypro3em-"


def device_mac() -> str:
    """Return a deterministic MAC-style identifier for this host."""
    mac_int = uuid.getnode()
    return f"{mac_int:012X}"


def device_id(mac: str | None = None) -> str:
    """Return an emulated device id for the given MAC."""
    mac_value = mac or device_mac()
    return f"{DEVICE_PREFIX}{mac_value.lower()}"
