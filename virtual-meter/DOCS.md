# Virtual Meter Add-on

## Overview

Emulates a Shelly Pro 3EM (Gen2) endpoint so a Hoymiles battery can read grid data sourced from another HTTP API.

## Configuration

- `http_port` (int): Port to bind the emulated HTTP API (default 80).
- `device_mac` (string, optional): Shelly-style MAC (no colons) for device id.
- `provider_endpoint` (string): HTTP endpoint to poll for source data.
- `provider_username` (string, optional): Username for provider endpoint authentication.
- `provider_password` (string, optional): Password for provider endpoint authentication.
- `poll_interval_ms` (int): Polling interval in milliseconds.
- `l1_act_power_json` / `l1_act_power_value`: L1 active power mapping/override.
- `l2_act_power_json` / `l2_act_power_value`: L2 active power mapping/override.
- `l3_act_power_json` / `l3_act_power_value`: L3 active power mapping/override.
- `debug_logging` (bool): Enable verbose debug logs.

## Networking

- `host_network: true` is required (binds directly to `http_port`).

## Supported RPC

- `/rpc` (JSON-RPC 2.0 + WebSocket upgrade)
- Methods used by the battery:
  - `Shelly.GetDeviceInfo`
  - `Shelly.GetStatus`
  - `EM.GetConfig`
  - `EM.GetStatus`
  - `EMData.GetStatus`

## Notes

- The implementation is intentionally minimal and only returns fields observed during testing.
