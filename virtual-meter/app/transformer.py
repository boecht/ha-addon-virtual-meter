"""Transform source readings into Shelly Gen2 output fields."""

from __future__ import annotations

from typing import Any


def _get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        if part not in current:
            return None
        current = current[part]
    return current


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
        if target.get(key) is None and value is not None:
            target[key] = value


def transform(
    source_json: dict[str, Any],
    json_paths: dict[str, str | None],
    overrides: dict[str, float | None],
    offsets: dict[str, float | None],
) -> dict[str, float]:
    """Merge source values with overrides and offsets."""
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
