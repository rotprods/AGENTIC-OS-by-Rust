# AGENTS — ROT Agentic OS

## Mission
Build the executable greenfield runtime for ACM vNext as an event-sourced, temporal, provenance-first, graph-native Agentic Operating System that survives context loss, agent death and cross-session replacement by construction.

## Authority boundaries
- `rot.knowledge`: constitutional governance and change-control.
- CP01: contract semantics reference.
- CP02: canonical identity semantics.
- CP03: durable event ledger semantics.
- COS 2.0 / `cos-graph-engine`: graph semantics and algorithms derived from accepted events.
- This repository: executable runtime implementation only.

## Hard laws
1. No graph mutation without an accepted event.
2. No canonical identity by name/fuzzy match.
3. No projection, vector index, UI, LLM output, GraphRAG extraction, ContextPack or Mission Control view is authority.
4. No irreversible action from stale head, stale event horizon, missing evidence or active barrier.
5. No source/provider writes during SHADOW phases.
6. One irreversible promotion at a time.
7. All critical cross-language contracts require Rust↔TypeScript↔Python golden parity before production authority.
8. Secrets and sensitive provider payloads must never enter Git, fixtures, prompts, graph attributes or embeddings.
9. Chat/model context is disposable. Durable project continuity must not depend on conversation history.
10. History is superseded, never silently rewritten.
11. Every material claim of VERIFIED/EMPIRICALLY_QUALIFIED requires revision-pinned evidence.
12. A successor needing the previous chat to continue is a continuity defect.

## Mandatory agent lifecycle
`BOOT → RECONCILE → CLAIM → HEARTBEAT → IMPLEMENT → EVIDENCE → CHECKPOINT → PREFLIGHT → HANDOFF → RELEASE`

Before material work, every agent MUST read `prompts/GRAPH_REFACTOR_V2.md` and `docs/AGENT_SURVIVAL_PROTOCOL_V2.md`, reconstruct live repository/event truth and create a unique Session identity.

Every CLAIM declares project/workstream/objective/session IDs, base SHA, expected contract version, semantic scopes, file/tree scopes, dependencies, authority ceiling, expected outputs and handoff target.

Every meaningful mutation writes through to all applicable durable planes during the same execution cycle: event/state/task/decision/evidence/checkpoint/graph inputs. Do not postpone continuity maintenance until session end when recovery cost has materially increased.

## Recovery SLO
A zero-context successor with repository access must reconstruct the North Star, current objective, exact source revision/event horizon, active ownership, blockers, evidence state and next safe action within <=5 minutes and one bounded ContextPack. Failure is a `CONTINUITY_DEFECT`.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

Authorized F1 surfaces:
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

Survival V2 SHADOW surfaces additionally include:
- `docs/AGENT_SURVIVAL_PROTOCOL_V2.md`
- `docs/ARCHITECTURE_V2.md`
- `docs/LEXICON.md`
- `plans/GRAPH_REFACTOR_V2_IMPLEMENTATION.md`
- `graph/`
- `state/`
- `templates/HANDOFF.md`
- `prompts/GRAPH_REFACTOR_V2.md`
- reference continuity contracts/tests under `python/rot_contracts` and `python/tests`

Do not begin PostgreSQL, production COS 2.0 port, GraphRAG, LangGraph runtime, GraphQL, MCP/A2A gateways or Mission Control UI before the applicable contract/parity gates pass. Interfaces may be specified; infrastructure is promoted only on measured triggers.

## F1 gate
Before F1 promotion, exact-head evidence must demonstrate:
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

## Survival V2 promotion ladder
`PROPOSED → IMPLEMENTED → EXECUTED → VERIFIED → EMPIRICALLY_QUALIFIED`

Minimum gates:
- G0 topology/live-truth reconciliation;
- G1 schema/contract validity;
- G2 deterministic reducer + replay/idempotency;
- G3 Rust↔TypeScript↔Python continuity parity;
- G4 COS projection rebuild parity;
- G5 checkpoint/handoff recovery parity;
- G6 concurrent claim/barrier correctness;
- G7 ContextPack freshness/invalidation;
- G8 zero-context death-drill SLO;
- later durable/multi-host gates only when justified by measured triggers.

Authority = min(Build, Assurance). Local green tests are evidence, never authority promotion by themselves.

## Handoff
Every completed wave records exact branch/head SHA, event watermark, commands/tests executed, exact outcomes, evidence hashes, graph/state/task/decision deltas, unresolved risks, released scopes, authority state and next safe action. The handoff is invalid if continuation requires prior chat history.
