# Virtual Meter Add-on

## Overview

This add-on emulates a Shelly Pro 3EM (Gen2) so a Hoymiles 1920 AC battery can
read grid data sourced from another HTTP endpoint (typically a Tasmota device).
It polls the upstream device, maps readings into Shelly EM fields, and serves
Shelly Gen2 JSON-RPC responses on the local network.

## How it works

1. The add-on polls `provider_endpoint` on a fixed interval.
2. The JSON response is parsed and mapped into L1/L2/L3 active power fields.
3. The add-on serves cached Shelly Gen2 responses over HTTP/WS at `/rpc`.
4. The device is advertised via mDNS for local discovery.

## Configuration

### Core settings

- `http_port` (int, default `80`): Port to bind the emulated HTTP API. The
  Hoymiles 1920 AC currently expects port 80, so changing this may prevent
  discovery or polling.
- `provider_endpoint` (string): HTTP endpoint to poll for source data.
- `provider_username` / `provider_password` (optional): If set, sent as query
  parameters `?user=...&password=...` on each poll.
- `poll_interval_ms` (int, minimum `250`): Poll interval in milliseconds.
  Most power meters update at 1 Hz, so `1000` ms is recommended.
- `device_mac` (optional): Shelly-style MAC (no colons). If unset, a deterministic
  host MAC is derived and normalized to Shelly format.
- `debug_logging` (bool): Enables verbose debug logs for RPC traffic.

### Power mapping

Each phase can be set using either a JSON path or a fixed value. If both are
present, the JSON path takes precedence. Fixed values are useful when only one
phase is supplied and the remaining phases should be set explicitly (for
example, `0.0`) without missing JSON paths being treated as errors. Offsets are
applied after mapping.

- `l1_act_power_json`, `l2_act_power_json`, `l3_act_power_json`
  - Dot-notation JSON paths into the provider payload.
  - Example: `StatusSNS.ENERGY.Power1`, `StatusSNS.ENERGY.Power2`,
    `StatusSNS.ENERGY.Power3`.
- `l1_act_power_value`, `l2_act_power_value`, `l3_act_power_value`
  - Fixed numeric values when a JSON path is not provided.
- `l1_power_offset`, `l2_power_offset`, `l3_power_offset`
  - Optional offsets (Watts) applied to mapped values.

### Example: Tasmota Status 10 mapping (single phase)

```yaml
provider_endpoint: "http://tasmota/cm?cmnd=Status%2010"
l1_act_power_json: "StatusSNS.ENERGY.Power"
l2_act_power_value: 0.0
l3_act_power_value: 0.0
poll_interval_ms: 1000
```

### Example: Tasmota with per-phase fields

```yaml
l1_act_power_json: "StatusSNS.ENERGY.Power1"
l2_act_power_json: "StatusSNS.ENERGY.Power2"
l3_act_power_json: "StatusSNS.ENERGY.Power3"
```

### Example: Offset tuning for solar on L1

If your solar panels are connected to L1 (phase 1), you can use an offset to
stabilize behavior:

- Set `l1_power_offset: -20` to bias the system toward a small net import.
  This targets about **20 W** consumption instead of **0 W**, which shifts the
  inevitable oscillation from import/export around zero into steady import.
  This is useful if export is not (well) compensated.
- Set `l1_power_offset: +20` to bias the system toward a small net export,
  keeping grid import near zero during generation and battery usage.

## Networking

- The add-on runs with host networking enabled so it can bind directly to
  `http_port`.
- The HTTP API listens on `/rpc` and supports JSON-RPC over HTTP and WebSocket.

## Supported RPC methods

The add-on serves the following Shelly Gen2 methods used by Hoymiles:

- `Shelly.GetDeviceInfo`
- `Shelly.GetStatus`
- `EM.GetConfig`
- `EM.GetStatus`
- `EMData.GetStatus`

## Logging

- `debug_logging: true` enables request/response logs for RPC calls and includes
  payloads. Use this to validate what the Hoymiles app is requesting.

## Troubleshooting

- **No data / zeros**: verify the JSON path matches the provider payload.
- **Provider errors**: check `provider_endpoint` and credentials; the poller
  logs fetch failures and keeps the last known good data.
- **Device not found**: confirm the add-on is running and that `http_port` is
  open.

## Notes

- This add-on intentionally implements the minimum Shelly Gen2 surface required
  by the Hoymiles integration. For example, it reports per-phase power only;
  frequency, current, and voltage are not provided.
