# Virtual Meter

The add-on provides a Shelly Pro 3EM (Gen2) emulator so that Hoymiles 1920 AC
battery owners can control battery charge and discharge based on grid
consumption data.

## What it does

- Polls a configurable HTTP endpoint (e.g., Tasmota Status 10).
- Maps source readings to Shelly EM fields using JSON paths or fixed values.
- Serves Shelly Gen2 JSON-RPC endpoints used by Hoymiles.
- Advertises the device via mDNS for local discovery.

## Configuration highlights

- `provider_endpoint` and optional `provider_username`/`provider_password`
- `poll_interval_ms` (minimum 250 ms)
- `l1/l2/l3_act_power_json` for JSON path mapping
- `l1/l2/l3_act_power_value` and `*_power_offset` for overrides/offsets
- `debug_logging` for verbose RPC/request logs
