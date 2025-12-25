"""JSON codec helpers for raw transport payloads."""

from __future__ import annotations

import json
from typing import Any


def decode(raw: bytes) -> dict[str, Any]:
    """Decode JSON bytes into a dictionary."""
    return json.loads(raw)


def encode(payload: dict[str, Any]) -> bytes:
    """Encode a dictionary into compact JSON bytes."""
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
