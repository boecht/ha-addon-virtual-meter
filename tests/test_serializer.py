from __future__ import annotations

from app.serializer import decode, encode


def test_encode_decode_roundtrip():
    payload = {"status": "ok", "value": 12.5}
    raw = encode(payload)
    decoded = decode(raw)

    assert decoded == payload
