from __future__ import annotations

import json

from app.config import load_settings


def test_load_settings_defaults_when_missing(tmp_path):
    missing_path = tmp_path / "options.json"
    settings = load_settings(path=str(missing_path))

    assert settings.provider_endpoint == ""
    assert settings.poll_interval_ms == 1000
    assert settings.http_port == 80
    assert settings.debug_logging is False


def test_load_settings_normalizes_empty_strings(tmp_path):
    options = {
        "provider_endpoint": "http://example",
        "poll_interval_ms": 1500,
        "provider_username": "",
        "provider_password": "",
        "device_mac": "",
        "l1_act_power_json": "StatusSNS.ENERGY.Power",
        "l1_act_power_value": "",
    }
    options_path = tmp_path / "options.json"
    options_path.write_text(json.dumps(options))

    settings = load_settings(path=str(options_path))

    assert settings.provider_endpoint == "http://example"
    assert settings.poll_interval_ms == 1500
    assert settings.provider_username is None
    assert settings.provider_password is None
    assert settings.device_mac is None
    assert settings.l1_act_power_json == "StatusSNS.ENERGY.Power"
    assert settings.l1_act_power_value is None
