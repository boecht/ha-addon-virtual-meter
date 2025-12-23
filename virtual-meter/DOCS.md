# Virtual Meter Add-on

## Overview

This add-on emulates a Shelly Pro 3EM (Gen2) device so a Hoymiles battery system can read grid data from an HTTP source.

## Configuration

- `http_port` (int): Port to bind the emulated HTTP API (default 80).
- `provider_endpoint` (string): HTTP endpoint to poll for source data.
- `poll_interval_ms` (int): Polling interval in milliseconds.
- `debug_logging` (bool): Enable verbose debug logs.

## Networking

- `host_network: true` is required. The emulator binds directly to port 80.

## Capture workflow (v0.0.1)

1. Install the add-on and configure your provider endpoint.
2. Start the add-on and open its Logs tab in Home Assistant.
3. Point the Hoymiles app to the add-on IP (port 80).
4. Observe and copy the JSON log lines to build the protocol capture logs.

## Supported RPC paths

- `/rpc/Shelly.GetStatus`
- `/rpc/EM.GetStatus?id=0`
- `/rpc/<method>` (result-only responses for supported Shelly Gen2 methods)
- `/rpc` (JSON-RPC 2.0 requests)
- `/shelly` (device info)

## Value resolution order

When building output values, the add-on uses this priority order:

1. JSON path values (`*_json`)
2. Numeric overrides (`*_value`)
3. Derived values (computed from available inputs)
4. Defaults from `defaults.json`

## Defaults

`defaults.json` provides fallback values for all required output fields.

## Notes

- v0.0.1 focuses on provider polling and mapping for protocol capture.
