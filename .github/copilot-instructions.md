# Virtual Meter – Always-Needed Implementation Context

## Purpose (do not deviate)
- Emulate a **Shelly Pro 3EM Gen2** on the local LAN so a **Hoymiles 192 AC** battery can read grid data sourced from a **Tasmota (Hichi IR) device**. (Source: "Product & Business Requirements")
- Provide a **reliable, always-on** emulator exposing required Shelly RPC endpoints and fields. (Source: "Product & Business Requirements")

## Non‑negotiable runtime/packaging constraints
- **Home Assistant add-on** runtime.
- **Python 3.13+ on Alpine Linux**.
- **host_network: true** and **bind port 80** directly; device must be reachable on LAN without ingress/port mapping.
- **No HA API dependency**; use local-only operation (no cloud/external dependencies). (Source: "Technical & Architectural Requirements")

## Required RPC surface (minimum viable behavior)
- Must serve HTTP GET RPC endpoints:
  - `GET /rpc/Shelly.GetStatus`
  - `GET /rpc/EM.GetStatus?id=0`
- Responses must be **valid Shelly Gen2 JSON-RPC style payloads** with correct field names/units. (Source: "Functional Requirements"; "Shelly Pro 3EM Gen2 API Reference")

## Required data fields (Hoymiles read targets)
- `total_act_power`
- `a_act_power`, `b_act_power`, `c_act_power`
- `voltage`, `current`, `pf`
(These must appear in the appropriate Shelly Gen2 structures/fields.) (Source: "Functional Requirements"; "Hoymiles 192 AC Assumptions & Validation Plan")

## Data acquisition + mapping rules
- Poll a **Tasmota** device at a configurable interval and map readings into Shelly EM fields.
- Support single‑phase vs three‑phase mapping:
  - **Single‑phase**: derive 3‑phase values from available data.
  - **Three‑phase**: map each phase explicitly.
- Allow optional per‑field data sources. If missing, use defaults or derive values (e.g., current from power/voltage). (Source: "Functional Requirements")

## Rate limiting + caching
- Rate-limit RPC responses to a configurable interval **not lower than the Tasmota read interval**.
- Serve **cached** readings when requests exceed the rate limit. (Source: "Functional Requirements"; "Technical & Architectural Requirements")

## Discovery + identity
- Advertise via **mDNS/zeroconf** (toggleable):
  - Service: `_http._tcp.local.`
  - TXT: `gen=2`, `app=Pro3EM`
- Use Python `zeroconf` library. (Source: "Functional Requirements"; "Technical & Architectural Requirements")

## Configuration surface (must exist)
- `tasmota_ip`, `poll_interval`
- `mock_mode`, `debug_logging`
- Phase mode + optional field mappings (see mapping rules above). (Source: "Technical & Architectural Requirements")

## Mock mode (always include when implementing behavior)
- Mock mode returns **static, valid JSON for the full API surface** (not only implemented endpoints).
- Mock mode logs every request for protocol analysis. (Source: "Functional Requirements")

## Scope boundaries (do not implement unless explicitly requested)
- No Shelly web UI or cloud features.
- No Shelly scripting, MQTT automation, or cloud integrations.
- No historical data storage beyond Hoymiles integration needs. (Source: "Product & Business Requirements")

## External client behavior assumptions (keep in mind)
- Hoymiles likely calls `GET /rpc/Shelly.GetStatus` and `GET /rpc/EM.GetStatus?id=0`.
- Poll cadence unknown; **protocol capture logs** should be used to confirm. (Source: "External Client Behavior"; "Hoymiles 192 AC Assumptions & Validation Plan")

## References (Notion)
- Project hub: https://www.notion.so/2d0344e4ba8b810c869aef8a98dcb1da
- Product & Business Requirements: https://www.notion.so/2d0344e4ba8b81df97ecfe2e632940af
- Functional Requirements: https://www.notion.so/2d0344e4ba8b813ea543c95637a0b22f
- Technical & Architectural Requirements: https://www.notion.so/2d0344e4ba8b811f98dec2d7b791d591
- Shelly Pro 3EM Gen2 API Reference: https://www.notion.so/2d1344e4ba8b818ebf12c255e8d34df2
- External Client Behavior: https://www.notion.so/2d1344e4ba8b8199a240e26a398907da
- Hoymiles 192 AC Assumptions & Validation Plan: https://www.notion.so/2d0344e4ba8b8163a1a1dcbdb70f528c
