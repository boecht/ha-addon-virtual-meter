"""Configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    """Typed settings for the add-on."""

    provider_endpoint: str
    provider_username: str | None = None
    provider_password: str | None = None
    device_mac: str | None = None
    poll_interval_ms: int
    http_port: int = 80
    l1_act_power_json: str | None = None
    l1_act_power_value: float | None = None
    l2_act_power_json: str | None = None
    l2_act_power_value: float | None = None
    l3_act_power_json: str | None = None
    l3_act_power_value: float | None = None
    debug_logging: bool = False


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def load_settings(path: str = "/data/options.json") -> Settings:
    """Load add-on options from disk."""
    options_path = Path(path)
    if not options_path.exists():
        return Settings(
            provider_endpoint="",
            poll_interval_ms=1000,
            debug_logging=False,
            http_port=80,
        )

    data = json.loads(options_path.read_text())
    normalized = {key: _normalize_value(value) for key, value in data.items()}
    return Settings(**normalized)
