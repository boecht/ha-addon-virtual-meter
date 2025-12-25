"""In-memory payload cache keyed by RPC method."""

from __future__ import annotations

from typing import Iterable

_payloads: dict[str, bytes] = {}


def set_payload(method: str, payload: bytes) -> None:
    """Store a serialized payload for a single method."""
    _payloads[method] = payload


def set_payloads(payloads: dict[str, bytes]) -> None:
    """Store serialized payloads for multiple methods."""
    _payloads.update(payloads)


def get_payload(method: str) -> bytes | None:
    """Retrieve a serialized payload for the given method."""
    return _payloads.get(method)


def list_methods() -> Iterable[str]:
    """Return the iterable of cached method names."""
    return _payloads.keys()
