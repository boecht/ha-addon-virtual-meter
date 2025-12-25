from __future__ import annotations

import uuid

from app import identity


def test_device_id_uses_prefix_and_lowercase():
    assert identity.device_id("ABCDEF123456") == "shellypro3em-abcdef123456"


def test_device_mac_uses_uuid_node(monkeypatch):
    monkeypatch.setattr(uuid, "getnode", lambda: 0xA1B2C3D4E5F6)
    assert identity.device_mac() == "A1B2C3D4E5F6"
