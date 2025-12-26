from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.assembler import build_dynamic_payloads
from app.config import Settings


def test_build_dynamic_payloads_merges_values_and_offsets():
    source = {
        "StatusSNS": {
            "ENERGY": {
                "Power": 123.4,
                "Power2": "56.7",
            }
        }
    }

    settings = Settings(
        provider_endpoint="http://example",
        poll_interval_ms=1000,
        l1_act_power_json="StatusSNS.ENERGY.Power",
        l2_act_power_json="StatusSNS.ENERGY.Power2",
        l3_act_power_json=None,
        l3_act_power_value=9.0,
        l2_power_offset=1.3,
    )

    now = datetime(2024, 1, 2, 12, 34, tzinfo=timezone.utc)
    payloads = build_dynamic_payloads(source, now, settings, device_mac="ABCDEF123456")

    assert set(payloads.keys()) == {"Shelly.GetStatus", "EM.GetStatus"}
    em_status = payloads["EM.GetStatus"]
    shelly_status = payloads["Shelly.GetStatus"]

    assert em_status["a_act_power"] == pytest.approx(123.4)
    assert em_status["b_act_power"] == pytest.approx(58.0)
    assert em_status["c_act_power"] == pytest.approx(9.0)

    assert shelly_status["sys"]["mac"] == "ABCDEF123456"
    assert shelly_status["sys"]["time"] == "12:34"
    assert shelly_status["sys"]["unixtime"] == int(now.timestamp())


def test_build_dynamic_payloads_falls_back_to_fixed_value():
    source = {"StatusSNS": {"ENERGY": {"Power": "oops"}}}

    settings = Settings(
        provider_endpoint="http://example",
        poll_interval_ms=1000,
        l1_act_power_json="StatusSNS.ENERGY.Power",
        l1_act_power_value=5.5,
    )

    now = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    payloads = build_dynamic_payloads(source, now, settings, device_mac="ABCDEF123456")

    assert payloads["EM.GetStatus"]["a_act_power"] == pytest.approx(5.5)


def test_build_dynamic_payloads_does_not_apply_offset_without_value():
    source = {}

    settings = Settings(
        provider_endpoint="http://example",
        poll_interval_ms=1000,
        l1_power_offset=12.0,
    )

    now = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    payloads = build_dynamic_payloads(source, now, settings, device_mac="ABCDEF123456")

    assert payloads["EM.GetStatus"]["a_act_power"] == pytest.approx(0.0)
