# CoPilot Instructions

This document is the authoritative LLM operations guide for this repo.

## Operating Requirements

### Project Principles

1. **Ground every statement in current evidence.**

  - Inspect the live repo/docs/logs before forming an opinion or recommending a change
  - Cite the exact file/line that supports your conclusion so nothing relies on memory or stale data

2. **Clarify, don’t guess**

  - Whenever something is unclear, inconsistent, or blocking the design goal, pause and
    ask the user a precise technical question instead of assuming or defaulting
  - Only follow a different approach if the prompt/mode explicitly demands it
  - Apply this discipline across all stages; requirements, system design, and implementation alike
  - Turn every ambiguity or spec gap into a targeted clarification
  - Treat uncertainty signals like "I think", "probably", or "maybe" as red flags that require clarification

3. **Build a Minimal Viable Product (MVP) as design goal — iterate and refine only if requested.**

  - Prioritize functionality and stability over broad compatibility
  - Avoid premature optimization for universal use cases
  - A larger implementation existed earlier; required behavior was validated and then reduced to the absolute
    minimum API that still works. Do not expand functionality unless Hoymiles requirements change.

4. **Quality and architecture trump backwards compatibility.**
  - Breaking changes are acceptable if they improve the codebase
  - Remove outdated patterns immediately; do not preserve legacy code
  - Avoid shortcuts; build the right solution once
  - Clean, maintainable architecture outranks legacy API stability

### Standard Workflow

#### Development Approach

- **Requirements Analysis**
  - Break down tasks into clear requirements, success criteria, and constraints
  - Evaluate feasibility with respect to API capabilities and project architecture
  - When uncertain, ask using the structured format
- **System Design**
  - Identify required modules, interfaces, integrations, and resources before coding
  - Map changes to source and target API specs
- **Implementation Strategy**
  - Choose TDD when tests exist or are requested
  - Otherwise implement directly, component by component
- **Quality Assurance**
  - Check against modular design principles, API compliance, and framework guidelines
  - Prefer targeted tests over full suite runs for speed

#### Development Best Practices

- Think step-by-step about goals, architecture, and limitations
- Prefer editing existing files over creating new ones
- Verify assumptions with data; never guess
- Run the smallest relevant tests for rapid feedback
- Execute pertinent tests after every change to catch regressions early

#### Quality Assurance Checklist

Every task must end with a QA review that compares all work to the initial task:

1. **Restate original task**: What did the user ask for?
2. **List file changes**: For each modified file, explain how the change serves the original task
3. **Identify misalignment**: Call out any changes that don't directly serve the task objective
4. **Reflect on alignment**: Does the complete set of changes accomplish what was requested?
  Are there gaps or overreach?
5. **Align documentation**: Do documentation and comments reflect any significant behaviour changes?
6. **Verify changes**: Read back edited content to confirm correctness

### Communication Protocol

#### Messaging Guidelines

- Be direct and technical; prioritize facts over tone
- Assume core programming literacy; skip over-explaining basics
- Flag bugs, performance issues, or maintainability risks immediately
- State opinions as such; do not present subjective preferences as facts

#### Structured Clarification Requests

When asking the user for clarification, follow this template:

```text
**Question X**: {Clear, specific question}
**Options**:
- A) {Option with trade-offs}
- B) {Option with trade-offs}
- C) {Additional options as needed}
**Context**: {Relevant best practices or constraints}
**Recommendation**: {Your recommendation with reasoning}
```

### External Sources

If Notion is accessible, consult it before web search.

### Source of Truth

This file is the canonical Copilot/LLM instruction set for the repository.
Keep other guidance documents (e.g., root `AGENTS.md`) pointing here to avoid drift.

## Implementation Overview

### Orientation & Quick Links

- Repo overview: `README.md`
- Add‑on overview: `virtual-meter/README.md`
- End‑user docs: `virtual-meter/DOCS.md`
- App entrypoint: `virtual-meter/app/main.py`
- RPC server: `virtual-meter/app/provider.py`
- Polling + mapping: `virtual-meter/app/consumer.py`, `virtual-meter/app/assembler.py`
- Tests / CI: `tests/`, `.github/workflows/`

### System Flow (Non‑Obvious)

- **Startup (one‑time, before serving):**

  - Normalize MAC → compute `device_id`.
  - Seed the cache with static payloads: `Shelly.GetDeviceInfo`, `EMData.GetStatus`, `EM.GetConfig`.
  - Start aiohttp app and poller task; start mDNS broadcaster.

- **Polling loop (repeats forever):**

  - HTTP GET to `provider_endpoint` (optional `user`/`password` query params).
  - Decode JSON → map values → assemble dynamic payloads.
  - Overwrite cache entries for `Shelly.GetStatus` and `EM.GetStatus`.
  - On fetch/parse errors: log and keep last good cache.

- **Serving phase (always):**
  - `/rpc` serves cached payloads only; there is no live computation on request.
  - HTTP and WebSocket paths both resolve from the same cache.

### RPC Surface (Methods Only)

Required methods:

- `Shelly.GetDeviceInfo`
- `Shelly.GetStatus`
- `EM.GetStatus`
- `EM.GetConfig`
- `EMData.GetStatus`

Transport:

- HTTP GET `/rpc?method=<MethodName>`
- HTTP POST `/rpc` with JSON body containing `method`
- WebSocket `/rpc` with JSON body containing `method`
- Unknown methods return JSON‑RPC error `-32601`

(Fields are defined in code; do not duplicate here.)

### Config → Behavior Map

- `provider_endpoint`, `provider_username`, `provider_password` → polling source and auth params
- `poll_interval_ms` → poll cadence and cache refresh rate
- `device_mac` → device identity and mDNS name
- `l1/l2/l3_*` mappings + offsets → power mapping behavior
- `debug_logging` → request/response logging
