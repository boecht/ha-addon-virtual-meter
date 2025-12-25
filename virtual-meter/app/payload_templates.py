"""Static payload templates used for one-time cache seeding."""

from __future__ import annotations

from .identity import DEVICE_PREFIX

DEVICE_INFO_TEMPLATE = {
    "id": f"{DEVICE_PREFIX}virtual",
    "mac": "000000000000",
    "model": "SPEM-003CEBEU",
    "gen": 2,
    "fw_id": "20241011-114455/1.4.4-g6d2a586",
    "ver": "1.4.4",
    "app": "Pro3EM",
    "auth_en": False,
    "auth_domain": None,
}

EMDATA_STATUS_TEMPLATE = {
    "id": 0,
}

EM_CONFIG_TEMPLATE = {
    "id": 0,
    "name": "Virtual Pro3EM",
}
