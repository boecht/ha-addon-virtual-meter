"""Assemble RPC payloads from source readings."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .config import Settings
from .payload_templates import EMDATA_STATUS_TEMPLATE


def _get_path(data: dict[str, Any], path: str) -> Any:
    """Traverse a dotted path in a nested mapping."""
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        if part not in current:
            return None
        current = current[part]
    return current


def _to_float(value: Any) -> float | None:
    """Convert a value to float if possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_json_values(
    target: dict[str, float | None],
    source: dict[str, Any],
    mappings: dict[str, str | None],
) -> None:
    """Apply JSON path mappings into the target values dict."""
    for key, path in mappings.items():
        if not path:
            continue
        value = _to_float(_get_path(source, path))
        if value is not None:
            target[key] = value


def _apply_value_overrides(
    target: dict[str, float | None], overrides: dict[str, float | None]
) -> None:
    """Apply static override values when input is missing."""
    for key, value in overrides.items():
        if target.get(key) is None and value is not None:
            target[key] = value


def _json_paths(settings: Settings) -> dict[str, str | None]:
    """Extract JSON path mappings from settings."""
    return {
        "l1_act_power": settings.l1_act_power_json,
        "l2_act_power": settings.l2_act_power_json,
        "l3_act_power": settings.l3_act_power_json,
    }


def _overrides(settings: Settings) -> dict[str, float | None]:
    """Extract fixed value overrides from settings."""
    return {
        "l1_act_power": settings.l1_act_power_value,
        "l2_act_power": settings.l2_act_power_value,
        "l3_act_power": settings.l3_act_power_value,
    }


def _offsets(settings: Settings) -> dict[str, float | None]:
    """Extract per-phase power offsets from settings."""
    return {
        "l1_act_power": settings.l1_power_offset,
        "l2_act_power": settings.l2_power_offset,
        "l3_act_power": settings.l3_power_offset,
    }


def _merge_values(
    source_json: dict[str, Any],
    settings: Settings,
) -> dict[str, float]:
    """Merge source values with overrides and offsets."""
    json_paths = _json_paths(settings)
    overrides = _overrides(settings)
    offsets = _offsets(settings)

    working: dict[str, float | None] = dict.fromkeys(json_paths.keys(), None)

    _apply_json_values(working, source_json, json_paths)
    _apply_value_overrides(working, overrides)
    for key, offset in offsets.items():
        if offset is None:
            continue
        if working.get(key) is None:
            continue
        working[key] = (working[key] or 0.0) + offset
    for key in working:
        if working[key] is None:
            working[key] = 0.0

    return {key: value for key, value in working.items() if value is not None}


def build_em_status(values: dict[str, float]) -> dict[str, Any]:
    """Build an EM.GetStatus payload from merged values."""
    return {
        "id": 0,
        "a_act_power": values.get("l1_act_power"),
        "b_act_power": values.get("l2_act_power"),
        "c_act_power": values.get("l3_act_power"),
    }


def build_dynamic_payloads(
    source_json: dict[str, Any],
    now: datetime,
    settings: Settings,
    device_mac: str,
) -> dict[str, dict[str, Any]]:
    """Build dynamic RPC payloads keyed by method name."""
    values = _merge_values(source_json, settings)
    em_status = build_em_status(values)
    sys_status = {
        "mac": device_mac,
        "time": now.strftime("%H:%M"),
        "unixtime": int(now.timestamp()),
    }
    shelly_status = {
        "sys": sys_status,
        "em:0": em_status,
        "emdata:0": dict(EMDATA_STATUS_TEMPLATE),
    }
    return {
        "Shelly.GetStatus": shelly_status,
        "EM.GetStatus": em_status,
    }
