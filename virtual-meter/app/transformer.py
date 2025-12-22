"""Transform source readings into Shelly Gen2 output fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TransformConfig:
    defaults: dict[str, float]


def _get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        if part not in current:
            return None
        current = current[part]
    return current


def _set_if_missing(target: dict[str, float | None], key: str, value: float | None) -> None:
    if target.get(key) is None and value is not None:
        target[key] = value


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_json_values(target: dict[str, float | None], source: dict[str, Any], mappings: dict[str, str | None]) -> None:
    for key, path in mappings.items():
        if not path:
            continue
        value = _to_float(_get_path(source, path))
        if value is not None:
            target[key] = value


def _apply_value_overrides(target: dict[str, float | None], overrides: dict[str, float | None]) -> None:
    for key, value in overrides.items():
        _set_if_missing(target, key, value)


def _derive_values(values: dict[str, float | None]) -> None:
    for phase in ("l1", "l2", "l3"):
        current = values.get(f"{phase}_current")
        voltage = values.get(f"{phase}_voltage")
        act_power = values.get(f"{phase}_act_power")
        aprt_power = values.get(f"{phase}_aprt_power")
        pf = values.get(f"{phase}_pf")

        if act_power is None and current is not None and voltage is not None:
            values[f"{phase}_act_power"] = current * voltage
        if current is None and act_power is not None and voltage:
            values[f"{phase}_current"] = act_power / voltage

        if aprt_power is None and act_power is not None and pf:
            values[f"{phase}_aprt_power"] = act_power / pf
        if pf is None and aprt_power is not None and act_power is not None and aprt_power:
            values[f"{phase}_pf"] = act_power / aprt_power

    if values.get("total_current") is None:
        total = sum(v for v in [values.get("l1_current"), values.get("l2_current"), values.get("l3_current")] if v is not None)
        if total > 0:
            values["total_current"] = total

    if values.get("n_current") is None:
        total = values.get("total_current")
        if total is not None:
            values["n_current"] = total

    if values.get("total_act_power") is None:
        total = sum(v for v in [values.get("l1_act_power"), values.get("l2_act_power"), values.get("l3_act_power")] if v is not None)
        if total > 0:
            values["total_act_power"] = total

    if values.get("total_aprt_power") is None:
        total = sum(v for v in [values.get("l1_aprt_power"), values.get("l2_aprt_power"), values.get("l3_aprt_power")] if v is not None)
        if total > 0:
            values["total_aprt_power"] = total


def _apply_defaults(values: dict[str, float | None], defaults: dict[str, float]) -> None:
    for key, value in defaults.items():
        _set_if_missing(values, key, value)


def transform(
    source_json: dict[str, Any],
    json_paths: dict[str, str | None],
    overrides: dict[str, float | None],
    defaults: dict[str, float],
    derive: bool = True,
) -> dict[str, float]:
    """Merge source values with overrides, derived values, and defaults."""
    working: dict[str, float | None] = dict.fromkeys(defaults.keys(), None)

    _apply_json_values(working, source_json, json_paths)
    _apply_value_overrides(working, overrides)
    if derive:
        _derive_values(working)
    _apply_defaults(working, defaults)

    return {key: value for key, value in working.items() if value is not None}


def em_status_from_values(values: dict[str, float]) -> dict[str, Any]:
    """Build EM.GetStatus response from merged values."""
    return {
        "id": 0,
        "a_current": values.get("l1_current"),
        "a_voltage": values.get("l1_voltage"),
        "a_act_power": values.get("l1_act_power"),
        "a_aprt_power": values.get("l1_aprt_power"),
        "a_pf": values.get("l1_pf"),
        "a_freq": values.get("l1_freq"),
        "a_errors": [],
        "b_current": values.get("l2_current"),
        "b_voltage": values.get("l2_voltage"),
        "b_act_power": values.get("l2_act_power"),
        "b_aprt_power": values.get("l2_aprt_power"),
        "b_pf": values.get("l2_pf"),
        "b_freq": values.get("l2_freq"),
        "b_errors": [],
        "c_current": values.get("l3_current"),
        "c_voltage": values.get("l3_voltage"),
        "c_act_power": values.get("l3_act_power"),
        "c_aprt_power": values.get("l3_aprt_power"),
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
