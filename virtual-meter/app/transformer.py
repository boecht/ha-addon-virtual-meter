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


def _set_if_missing(
    target: dict[str, float | None], key: str, value: float | None
) -> None:
    if target.get(key) is None and value is not None:
        target[key] = value


def _to_float(value: Any) -> float | None:
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
    for key, path in mappings.items():
        if not path:
            continue
        value = _to_float(_get_path(source, path))
        if value is not None:
            target[key] = value


def _apply_value_overrides(
    target: dict[str, float | None], overrides: dict[str, float | None]
) -> None:
    for key, value in overrides.items():
        _set_if_missing(target, key, value)


def _derive_values(values: dict[str, float | None]) -> None:
    for phase in ("l1", "l2", "l3"):
        act_power = values.get(f"{phase}_act_power")
        aprt_power = values.get(f"{phase}_aprt_power")
        current = values.get(f"{phase}_current")
        pf = values.get(f"{phase}_pf")
        voltage = values.get(f"{phase}_voltage")

        if act_power is None and current is None:
            act_power = 0.0
            values[f"{phase}_act_power"] = act_power
        if act_power is None and current is not None and voltage is not None:
            act_power = current * voltage
            values[f"{phase}_act_power"] = act_power
        if act_power is not None and current is None and voltage is not None:
            values[f"{phase}_current"] = 0.0 if voltage == 0 else act_power / voltage
        if act_power is not None and current is not None and voltage is None:
            values[f"{phase}_voltage"] = 0.0 if current == 0 else act_power / current
        if act_power is not None and aprt_power is None and pf is not None:
            values[f"{phase}_aprt_power"] = 0.0 if pf == 0 else act_power / pf
        if act_power is not None and aprt_power is not None and pf is None:
            values[f"{phase}_pf"] = 0.0 if aprt_power == 0 else act_power / aprt_power


def _derive_totals(values: dict[str, float | None]) -> None:
    if values.get("total_current") is None:
        vals = [
            v
            for v in [
                values.get("l1_current"),
                values.get("l2_current"),
                values.get("l3_current"),
            ]
            if v is not None
        ]
        if vals:
            values["total_current"] = sum(vals)

    if values.get("total_act_power") is None:
        vals = [
            v
            for v in [
                values.get("l1_act_power"),
                values.get("l2_act_power"),
                values.get("l3_act_power"),
            ]
            if v is not None
        ]
        if vals:
            values["total_act_power"] = sum(vals)

    if values.get("total_aprt_power") is None:
        vals = [
            v
            for v in [
                values.get("l1_aprt_power"),
                values.get("l2_aprt_power"),
                values.get("l3_aprt_power"),
            ]
            if v is not None
        ]
        if vals:
            values["total_aprt_power"] = sum(vals)

    if values.get("n_current") is None:
        total = values.get("total_current")
        if total is not None:
            values["n_current"] = total


def _apply_defaults(
    values: dict[str, float | None], defaults: dict[str, float]
) -> None:
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
    _derive_values(working)
    _derive_totals(working)

    return {key: value for key, value in working.items() if value is not None}
