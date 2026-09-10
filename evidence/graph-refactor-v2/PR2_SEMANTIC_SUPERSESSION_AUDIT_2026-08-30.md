# PR #2 Semantic Supersession Audit — 2026-08-30

Authority: migration evidence for topology cleanup. This document does not erase PR #2; it maps every unique PR #2 file to an explicit V2 destination before closure.

## Compared revisions
- historical Survival V1 PR #2 head: `6d9c3111891b8359296f60c02294ed1d251b0889`
- active Survival V2 branch: `feat/graph-refactor-v2-survival`
- merge base of PR #2 and V2 lineage: `4964721c48f62cefe5593837fed7dacfd1945253`
- unique PR #2 commits: 7
- unique PR #2 file surface: 7 paths

## File-by-file semantic mapping

| PR #2 unique path | V2 disposition | V2 authority/replacement | Rationale |
|---|---|---|---|
| `AGENTS.md` | SUPERSEDE | current `AGENTS.md` | V2 preserves disposable-chat law, authority hierarchy, mandatory lifecycle, write-through, recovery SLO, evidence discipline and explicit promotion gates; it is stricter and tied to F1 + Survival V2. |
| `docs/AGENT_SURVIVAL_PROTOCOL.md` | SUPERSEDE | `docs/AGENT_SURVIVAL_PROTOCOL_V2.md` | V2 retains North Star, authority hierarchy, one-truth/many-projections, durable planes, lifecycle, checkpoint triggers, COS projection law, recovery/death drill and measured-trigger overengineering policy. |
| `graph/ONTOLOGY.md` | SUPERSEDE | `graph/ONTOLOGY_V2.md` + `graph/projection_manifest.json` | V2 expands typed node/edge semantics, temporal metadata and explicit COS dimension activation/NOT_APPLICABLE policy. |
| `prompts/AGENT_SURVIVAL_METAPROMPT.md` | MIGRATE THEN SUPERSEDE | `prompts/AGENT_SURVIVAL_METAPROMPT_V2.md` | This was the only standalone operational interface not previously preserved 1:1. V2 migration now retains boot/reconcile/claim/write-through/checkpoint/evidence/ContextPack/preflight/handoff/self-audit/completion laws while adding state-hash binding, strict event horizon, logical-time authority boundary, UNTRUSTED_DATA handling and synthetic-vs-empirical death-drill distinction. |
| `schemas/checkpoint.schema.json` | SUPERSEDE | `schemas/survival-checkpoint.v2.schema.json` | V1 allowed extra fields, string watermark, partial SHAs and no canonical state binding. V2 is closed-schema, uses strict integer watermark/full SHA, distinguishes test statuses and requires tamper-evident `checkpoint_hash` + `state_hash`. |
| `schemas/project_state.schema.json` | SUPERSEDE | `schemas/survival-project-state.v2.schema.json` | V1 allowed extra fields and coarse summaries. V2 uses bounded typed collections, exact authority vocabulary, full observed semantic SHA, integer event watermark, explicit verified/unverified capabilities and bounded next-safe-actions. |
| `templates/HANDOFF.md` | SUPERSEDE | current `templates/HANDOFF.md` + root `HANDOFF.md` | V2 retains identity, authority snapshot, completed work, exact tests/evidence, blockers, graph/task deltas and resume recipe while adding live-truth invalidation and `NEXT_ITERATION_METAPROMPT` semantics. |

## Preserved V1 laws
The audit explicitly checked preservation of the highest-value V1 semantics:
- chat/model context is non-authoritative and disposable;
- zero-context successor recovery is a hard requirement;
- boot must reconstruct current durable truth before mutation;
- every write has a semantic/file ownership claim;
- meaningful mutations write through to durable continuity planes in the same work cycle;
- checkpoint cadence is driven by recovery cost/state transition rather than message count;
- tests/evidence require exact revision/run identity and distinguish failed/skipped/not-run;
- ideas/refactor debt are durable nodes rather than forgotten prose;
- graph projections are derived and cannot become hidden authority;
- Event Sourcing is the authority path for graph mutation;
- ContextPack is a bounded invalidatable cache;
- irreversible actions require fresh preflight;
- handoff is invalid when prior chat is required;
- completion requires deliverable + evidence + state/graph/task/decision continuity.

## V2 hardening beyond V1
V2 additionally closes weaknesses discovered by the gauntlet:
- `state_hash` binds checkpoints to canonical reducer output;
- accepted-event sequence gaps fail closed;
- freshness projection binding is symmetric;
- same event identity/different payload fails closed across calls;
- projection rebuild has deterministic hash parity tests;
- claims use monotonic fencing generations and reject stale/read-only writers;
- logical ticks are explicitly reference coordinates, never distributed clock authority;
- ContextPack external/imported payload is `UNTRUSTED_DATA`, bounded by depth/item/string/serialized-byte limits;
- synthetic death-drill success cannot self-promote empirical successor authority;
- duplicate promotion routes are superseded rather than left open.

## Decision
All seven unique PR #2 file semantics are now either preserved and strengthened in V2 or explicitly migrated. No PR #2-only semantic requirement remains without a V2 owner.

Therefore PR #2 is safe to close as `SUPERSEDED_UNMERGED_HISTORY` once live GitHub confirms the replacement files are present. Closure is metadata/history cleanup only: PR #2 remains queryable and its commits are not rewritten or deleted.
