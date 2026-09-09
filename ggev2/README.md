# /GGEV2 — Global Graph Execution V2 Realtime Control Plane

Authority: DERIVED / REBUILDABLE / READ_ONLY
Owner: AGENTIC-OS-by-Rust
Status: IMPLEMENTED_SHADOW
Source revision: d19009055fb86e33836706fd0f09991869311431

## Purpose

/GGEV2 compiles current operational truth into one bounded machine-readable realtime projection for humans and agents. It is not an event ledger, not canonical state, not governance authority and not a mutation path.

Canonical direction:

```
GitHub live truth
+ accepted events (when qualified)
+ project_state/checkpoints
+ governance manifests
+ exact-head evidence
+ active claims
        ↓
    GGEV2 compiler
        ↓
REALTIME_STATE + graphs + drift + handoff
```

Reverse authority is forbidden:

```
GGEV2 projection ─X→ canonical authority
```

## Contract

Every compiled snapshot declares:

- `generated_at`
- `source_revision`
- `event_watermark`
- `projection_revision`
- `freshness`
- `authority_state`
- `source_observations`
- `active_objectives`
- `active_workstreams`
- `active_claims`
- `blockers`
- `governance`
- `quality_gates`
- `graph`
- `drift`
- `next_safe_actions`
- `state_hash`

Unknown/unreachable data is represented as `UNKNOWN`, `UNRESOLVED`, `STALE` or `BLOCKED`; never inferred as green.

## Freshness

A snapshot is `FRESH` only when every required source observation matches the compiler's expected source locator/revision policy. A source change invalidates the snapshot until recompilation.

`REALTIME_STATE.json` is therefore evidence of a compilation at a revision, not a permanently-current truth claim.

## Core surfaces

- `SOURCE_REGISTRY.json` — what sources may contribute and their authority role.
- `AUTHORITY_MAP.json` — authority hierarchy and forbidden reverse writes.
- `DRIFT_RULES.json` — explicit stale/drift classifications.
- `REALTIME_STATE.json` — current persisted projection snapshot.
- `GRAPH_INDEX.json` — shared-ID graph projection.
- `BLOCKERS.json` — blocker queue extracted from the same snapshot.
- `HANDOFF_REALTIME.md` — zero-context recovery summary.
- `schema/realtime-state.schema.json` — machine contract.
- `python/rot_ai/ggev2.py` — deterministic compiler.

## Invariants

1. No hidden source of truth.
2. No projection self-promotion.
3. Same canonical input => same semantic `state_hash`.
4. `generated_at` never participates in semantic state hash.
5. Stale source revision => `freshness != FRESH`.
6. Unqualified durable event authority => event watermark remains whatever canonical state declares; GGEV2 cannot advance it.
7. Missing hard-gate evidence remains a blocker.
8. Graph nodes and edges are derived only from source fields included in the same snapshot.
9. A cold agent can recover the current bounded frontier from `/GGEV2` without chat context, but must reread live authority before mutation.
