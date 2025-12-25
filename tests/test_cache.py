from __future__ import annotations

from app import cache


def setup_function():
    cache._payloads.clear()


def test_set_and_get_payload():
    cache.set_payload("Shelly.GetStatus", b"payload")
    assert cache.get_payload("Shelly.GetStatus") == b"payload"


def test_set_payloads_and_list_methods():
    cache.set_payloads({"A": b"one", "B": b"two"})
    assert cache.get_payload("A") == b"one"
    assert cache.get_payload("B") == b"two"
    assert set(cache.list_methods()) == {"A", "B"}
