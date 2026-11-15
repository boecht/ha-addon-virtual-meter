# Changelog

## 1.1.1

- Fixed malformed `/rpc` requests: a POST body that is not JSON (including empty or
  non-UTF-8 bodies) now gets HTTP 400 with JSON-RPC error `-32700`, and JSON that is not
  an object gets HTTP 400 with `-32600`; on WebSocket, a non-object message gets `-32600`
  and the connection stays open. These requests no longer log a stack trace.

## 1.1.0

- Added `GET /shelly` device info responses for discovery compatibility.
- Fixed provider timeouts to log as warnings (including timeout duration).

## 1.0.0

- First published release of the Virtual Meter add-on.
- Emulates Shelly Pro 3EM (Gen2) JSON-RPC endpoints for Hoymiles 1920 AC.
- Polls a configurable HTTP provider (e.g., Tasmota Status 10).
- Supports per-phase JSON path mapping, fixed overrides, and power offsets.
- Includes mDNS discovery and debug logging for troubleshooting.
