# AGENTIC-OS-by-Rust

Executable greenfield runtime for ROT Agentic OS / ACM vNext.

## North Star
Given only a ProjectID, ObjectiveID, AgentID, RepositoryID or ConversationID, any authorized cold runtime can reconstruct the same bounded state, event horizon, ownership, evidence, graph context and next safe action without hidden chat memory or UI/projection authority.

## Zero-context bootstrap
Read in this order:
1. `AGENTS.md` — laws, authority, lifecycle, current phase.
2. `prompts/GRAPH_REFACTOR_V2.md` — mandatory graph-refactor/gauntlet operating protocol.
3. `GOAL.md` and `goal-state.json` — North Star + F1 gate.
4. `STATE.md` + `state/project_state.json` — current projected state; verify freshness before use.
5. `TASKS.md` — executable frontier and blockers.
6. `docs/ARCHITECTURE_V2.md` + `docs/AGENT_SURVIVAL_PROTOCOL_V2.md` — V2 architecture and continuity semantics.
7. `docs/LEXICON.md` + `graph/ONTOLOGY_V2.md` — canonical vocabulary and typed graph model.
8. latest evidence/CI + open PR lifecycle — live GitHub outranks stale projections.
9. `HANDOFF.md` — current resume recipe.

## Current topology
`main` is intentionally tiny. PR #1 contains the F1 contract kernel. PR #3 is the current combined F1 + Agent Survival V2 candidate and is the only branch intended to prove the integrated architecture before any supersession decision.

## Authority
- constitutional/change-control: `rot.knowledge` and CP references;
- executable contracts/identity/event semantics: F1 kernel in this repository;
- accepted event + verified evidence: durable operational authority when promoted;
- canonical state: deterministic reducer output;
- COS/GraphRAG/ContextPack/UI: rebuildable projections/caches, never reverse-write authority;
- chat/model memory: advisory only.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`.

No PostgreSQL, production COS port, GraphRAG runtime, LangGraph, GraphQL, MCP/A2A or Mission Control promotion is authorized by Survival V2. Infrastructure requires measured triggers.

## Verification commands
F1 CI currently runs:
- Rust format/clippy/tests;
- Python golden/schema tests;
- TypeScript compile/golden/schema tests.

Survival V2 extends Python discovery with deterministic reducer, freshness, checkpoint and death-drill tests. Cross-language Survival parity remains a later explicit gate.

## Recovery SLO
A zero-context successor should reconstruct the bounded current truth and next safe action in <=5 minutes and <=1 bounded ContextPack. Failure is a `CONTINUITY_DEFECT`.
