# /GGEV2 Refresh Protocol v1

Authority: DERIVED / READ_ONLY

## Goal

Recompile `/GGEV2` whenever a material source revision changes. Never patch `REALTIME_STATE.json` by hand as an authority action.

## BOOT

Before compiling, reread:

1. live GitHub PR/branch head;
2. `state/project_state.json`;
3. dynamically resolved latest valid checkpoint;
4. `governance/external-authorities.v2.json` or its current successor;
5. required exact-head quality gates;
6. active claims/workstreams where available.

## Observation input

The collector creates a temporary JSON object:

```json
{
  "source_revision": "<40-hex live head>",
  "observations": [
    {"source_id":"github_live","status":"FRESH","revision":"<head>","evidence_refs":["..."]},
    {"source_id":"project_state","status":"FRESH","revision":"<blob sha>","evidence_refs":["state/project_state.json"]},
    {"source_id":"checkpoints","status":"FRESH","revision":"<checkpoint id>","evidence_refs":["..."]},
    {"source_id":"governance_manifest","status":"BLOCKED","revision":"<blob sha>","evidence_refs":["..."]}
  ]
}
```

Status must describe semantic usability, not merely HTTP availability. A readable governance manifest with unresolved promotion blockers may correctly be `BLOCKED`.

## Compile

```bash
PYTHONPATH=python python -m rot_ai.ggev2_cli \
  --project-state state/project_state.json \
  --observations /tmp/ggev2-observations.json \
  --governance /tmp/ggev2-governance-summary.json \
  --quality-gates /tmp/ggev2-quality-gates.json \
  --projection-revision <N> \
  --output ggev2/REALTIME_STATE.json
```

The compiler derives graph topology and drift. `generated_at` changes between runs; semantic `state_hash` must not change when semantic input is unchanged.

## Validate

Run:

```bash
PYTHONPATH=python python -m unittest python/tests/test_ggev2.py -v
```

and validate `REALTIME_STATE.json` against `ggev2/schema/realtime-state.schema.json`.

## Freshness policy

- required source missing → `BLOCKED`;
- live head differs → `STALE`;
- event watermark differs → `STALE`;
- governance unresolved → `BLOCKED`;
- exact-head required quality evidence incomplete → `BLOCKED` or `STALE` according to source semantics;
- all required observations current and usable → `FRESH`.

## Mutation preflight

A runtime may use GGEV2 to decide what it should reread. It may not use GGEV2 alone to authorize mutation. Before writing, reread authoritative live sources and compare revisions.

## Persistence

When persisting a refreshed projection also regenerate or verify:

- `BLOCKERS.json`;
- `GRAPH_INDEX.json`;
- `HANDOFF_REALTIME.md`.

Any mismatch between these surfaces and `REALTIME_STATE.state_hash` is projection drift and must fail closed.
