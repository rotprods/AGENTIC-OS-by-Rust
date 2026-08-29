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
3. No projection, vector index, UI, LLM output, GraphRAG extraction, ContextPack, or Mission Control view is authority.
4. No irreversible action from stale head, stale event horizon, missing evidence, or active barrier.
5. No source/provider writes during SHADOW phases.
6. One irreversible promotion at a time.
7. All critical cross-language contracts require Rust↔TypeScript↔Python golden parity.
8. Secrets and sensitive provider payloads must never enter Git, fixtures, prompts, graph attributes, embeddings, checkpoints, or handoffs.
9. Chat context is disposable. Any fact required for safe continuation must be persisted before recovery cost becomes material.
10. Decisions, assumptions, evidence, ideas and refactor debt are append-only/supersedable durable objects; never silently overwrite history.

## Mandatory survival bootstrap
Before substantial work, read and obey:
1. `prompts/AGENT_SURVIVAL_METAPROMPT.md`
2. `docs/AGENT_SURVIVAL_PROTOCOL.md`
3. `graph/ONTOLOGY.md`
4. current canonical state/checkpoint/handoff/claims for the target project/workstream.

The survival metaprompt is a mandatory execution contract, not optional documentation.

## Mandatory agent lifecycle
`BOOT → RECONCILE → CLAIM → HEARTBEAT → EXECUTE → EVIDENCE → CHECKPOINT → PREFLIGHT → HANDOFF → RELEASE`

Every CLAIM declares project/workstream/objective IDs, agent/session IDs, base SHA, expected contract version, semantic scopes, file/tree scopes, dependencies, authority ceiling and handoff target.

Every meaningful mutation MUST write through to the applicable durable layers in the same work cycle: event ledger, canonical state, task state, decision history, graph projection inputs, test/evidence ledger and checkpoint when recovery cost materially increases.

## Continuity SLO
A zero-context successor should be able to identify the safe next action in <=5 minutes using repository/durable state without access to prior chat history. Treat failure of this SLO as a continuity defect.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL / SHADOW_ONLY`

Do not begin PostgreSQL, COS 2.0 port, GraphRAG, LangGraph runtime, GraphQL, MCP/A2A gateways, or Mission Control UI before `G1_CONTRACT_PARITY` passes.
