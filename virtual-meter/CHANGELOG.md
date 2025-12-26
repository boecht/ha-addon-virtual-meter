# Changelog

## 1.1.0

- Added `GET /shelly` device info responses for discovery compatibility.
- Fixed provider timeouts to log as warnings (including timeout duration).

## 1.0.0

- First published release of the Virtual Meter add-on.
- Emulates Shelly Pro 3EM (Gen2) JSON-RPC endpoints for Hoymiles 1920 AC.
- Polls a configurable HTTP provider (e.g., Tasmota Status 10).
- Supports per-phase JSON path mapping, fixed overrides, and power offsets.
- Includes mDNS discovery and debug logging for troubleshooting.
