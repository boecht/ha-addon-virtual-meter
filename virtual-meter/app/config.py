"""Configuration loading and validation (stub).

Pseudocode notes:
- Home Assistant add-ons provide options via /data/options.json
- Use Pydantic to validate and coerce types
- Keep defaults aligned with config.yaml options
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

DEFAULTS_PATH = Path("defaults.json")


class Settings(BaseModel):
    """Typed settings for the add-on."""

    provider_endpoint: str
    provider_username: str | None = None
    provider_password: str | None = None
    poll_interval_ms: int
    mock_mode: bool = False
    http_port: int = 80
    l1_current_json: str | None = None
    l1_current_value: float | None = None
    l1_voltage_json: str | None = None
    l1_voltage_value: float | None = None
    l1_act_power_json: str | None = None
    l1_act_power_value: float | None = None
    l1_aprt_power_json: str | None = None
    l1_aprt_power_value: float | None = None
    l1_pf_json: str | None = None
    l1_pf_value: float | None = None
    l1_freq_json: str | None = None
    l1_freq_value: float | None = None
    l2_current_json: str | None = None
    l2_current_value: float | None = None
    l2_voltage_json: str | None = None
    l2_voltage_value: float | None = None
    l2_act_power_json: str | None = None
    l2_act_power_value: float | None = None
    l2_aprt_power_json: str | None = None
    l2_aprt_power_value: float | None = None
    l2_pf_json: str | None = None
    l2_pf_value: float | None = None
    l2_freq_json: str | None = None
    l2_freq_value: float | None = None
    l3_current_json: str | None = None
    l3_current_value: float | None = None
    l3_voltage_json: str | None = None
    l3_voltage_value: float | None = None
    l3_act_power_json: str | None = None
    l3_act_power_value: float | None = None
    l3_aprt_power_json: str | None = None
    l3_aprt_power_value: float | None = None
    l3_pf_json: str | None = None
    l3_pf_value: float | None = None
    l3_freq_json: str | None = None
    l3_freq_value: float | None = None
    n_current_json: str | None = None
    n_current_value: float | None = None
    total_current_json: str | None = None
    total_current_value: float | None = None
    total_act_power_json: str | None = None
    total_act_power_value: float | None = None
    total_aprt_power_json: str | None = None
    total_aprt_power_value: float | None = None
    debug_logging: bool = False
    defaults: dict[str, Any] = {}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _load_defaults(path: Path = DEFAULTS_PATH) -> dict[str, Any]:
    candidates = [
        path,
        Path("/app/defaults.json"),
        Path(__file__).resolve().parents[1] / "defaults.json",
    ]
    logger = logging.getLogger("virtual_meter.config")
    for candidate in candidates:
        logger.debug("Checking defaults path: %s", candidate)
        if candidate.exists():
            logger.info("Using defaults file: %s", candidate)
            return json.loads(candidate.read_text())
    logger.warning("No defaults.json found; using empty defaults")
    return {}


def load_settings(path: str = "/data/options.json") -> Settings:
    """Load add-on options from disk.

    Pseudocode:
    - Read JSON from /data/options.json
    - Merge with defaults
    - Return Settings model
    """
    options_path = Path(path)
    defaults = _load_defaults()
    logging.getLogger("virtual_meter.config").info("Loaded defaults keys: %s", sorted(defaults.keys()))
    if not options_path.exists():
        # Fall back to defaults for local dev
        return Settings(
            provider_endpoint="",
            poll_interval_ms=1000,
            mock_mode=False,
            debug_logging=False,
            http_port=80,
            defaults=defaults,
        )

    data = json.loads(options_path.read_text())
    normalized = {key: _normalize_value(value) for key, value in data.items()}
    normalized["defaults"] = defaults
    return Settings(**normalized)
