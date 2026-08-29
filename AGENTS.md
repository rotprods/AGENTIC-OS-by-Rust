# AGENTS — ROT Agentic OS

## Mission
Build the executable greenfield runtime for ACM vNext as an event-sourced, temporal, provenance-first, graph-native Agentic Operating System.

## Authority boundaries
- `rot.knowledge`: constitutional governance and change-control.
- CP01: contract semantics reference.
- CP02: canonical identity semantics.
- CP03: durable event ledger semantics.
- COS 2.0: graph semantics and algorithms derived from events.
- This repository: executable runtime implementation only.

## Hard laws
1. No graph mutation without an accepted event.
2. No canonical identity by name/fuzzy match.
3. No projection, vector index, UI, LLM output, GraphRAG extraction, or Mission Control view is authority.
4. No irreversible action from stale head, stale event horizon, missing evidence, or active barrier.
5. No source/provider writes during SHADOW phases.
6. One irreversible promotion at a time.
7. All critical cross-language contracts require Rust↔TypeScript↔Python golden parity.
8. Secrets and sensitive provider payloads must never enter Git, fixtures, prompts, graph attributes, or embeddings.

## Mandatory agent lifecycle
`BOOT → CLAIM → HEARTBEAT → EVIDENCE → PREFLIGHT → HANDOFF`

Every CLAIM declares project/workstream/objective IDs, base SHA, expected contract version, semantic scopes, file/tree scopes, dependencies, authority ceiling and handoff target.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL / SHADOW_ONLY`

Authorized surfaces:
- `crates/rot-id`
- `crates/rot-contracts`
- `crates/rot-canonical-json`
- `crates/rot-hash`
- `crates/rot-temporal`
- `crates/rot-provenance`
- `crates/rot-event`
- `schemas/`
- `fixtures/golden/`
- parity implementations under `packages/contracts-ts` and `python/rot_contracts`

Do not begin PostgreSQL, COS 2.0 port, GraphRAG, LangGraph runtime, GraphQL, MCP/A2A gateways, or Mission Control UI before `G1_CONTRACT_PARITY` passes.

## F1 gate
Before promotion, exact-head evidence must demonstrate:
- canonical bytes Rust↔TypeScript↔Python: 100%;
- SHA-256 parity: 100%;
- schema accept/reject parity: 100%;
- critical line/branch/function coverage: 100%;
- changed-line coverage: 100%;
- critical mutation kill: 100%;
- requirement traceability: 100%;
- secret leakage: 0;
- tenant/scope leakage: 0;
- nondeterministic golden divergence: 0;
- P0/P1: 0.

## Handoff
Every completed wave records exact branch/head SHA, commands executed, evidence hashes, known gaps, authority state and the next safe action. Local green tests are evidence, never authority promotion.
