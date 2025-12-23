# ha-addon-virtual-meter

Home Assistant add-on repository for a virtual Shelly Pro 3EM (Gen2) emulator.

## Goals
- Emulate Shelly Pro 3EM Gen2 RPC endpoints used by Hoymiles battery systems.
- Pull grid data from a configurable HTTP provider endpoint.
- Normalize/derive values into Shelly-compatible fields.

## Structure
- `repository.json` - Supervisor metadata
- `virtual-meter/` - Add-on folder

## Status
Active development: provider polling and mapping are implemented with configurable inputs and defaults.
