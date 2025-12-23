# Virtual Meter Add-on

## Overview

This add-on emulates a Shelly Pro 3EM (Gen2) device so a Hoymiles battery system can read grid data from an HTTP source.

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

- `host_network: true` is required. The emulator binds directly to port 80.

## Capture workflow (v0.0.1)

1. Install the add-on and configure your provider endpoint.
2. Start the add-on and open its Logs tab in Home Assistant.
3. Point the Hoymiles app to the add-on IP (port 80).
4. Observe and copy the JSON log lines to build the protocol capture logs.

## Supported RPC paths

- `/rpc` (JSON-RPC 2.0 requests + WebSocket upgrade)

## Notes

- v0.0.1 focuses on provider polling and mapping for protocol capture.
