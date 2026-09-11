# /GGEV2 Realtime Handoff

Authority: DERIVED / READ_ONLY
Snapshot state hash: `sha256:7edeb148f42b076948e2619639700f16ff18390d870dbfc99303a6b19e2ecb8d`
Source revision: `d19009055fb86e33836706fd0f09991869311431`
Projection revision: `1`
Freshness: `BLOCKED`

## North Star

Any authorized zero-context runtime can reconstruct the same bounded state, event horizon, ownership, evidence, graph context and next safe action without hidden chat memory.

## Current bounded truth

- Project: `rot://project/agentic-os`
- Objective: `rot://objective/agentic-os/survival-v2-cp15-governance-candidate-resolution`
- Workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- Authority: `IMPLEMENTED / SHADOW_ONLY`
- Event watermark: `0`
- Canonical active Survival PR at snapshot compile time: `rotprods/AGENTIC-OS-by-Rust#4`
- Exact source head observed: `d19009055fb86e33836706fd0f09991869311431`

## Why freshness is BLOCKED

The source observations themselves are revision-bounded, but external governance remains incomplete:

- `rot.knowledge` — PINNED
- `COS2` — PINNED
- `CP01` — CANDIDATE_PINNED
- `CP02` — CANDIDATE_PINNED
- `CP03` — CANDIDATE_PINNED

Additionally GitHub promotion enforcement and signed-head enforcement are not active, and the genuine independent death drill is not yet empirically passed.

## Hard blockers

1. CP01/CP02/CP03 governance not promotion-qualified.
2. Genuine independent zero-context death drill not executed.
3. Durable accepted-event authority not qualified.
4. GitHub promotion enforcement not active.
5. Signed-head enforcement not active.

## Next safe actions

1. Reread live GitHub PR #4 head before any mutation.
2. Reread `state/project_state.json`, latest valid checkpoint and `governance/external-authorities.v2.json`.
3. If any revision differs from `REALTIME_STATE.json`, mark this snapshot `STALE` and recompile before continuing.
4. Resolve external governance promotion blockers in their own authority plane.
5. Configure GitHub promotion enforcement through an authorized control-plane write path.
6. Execute the empirical zero-context successor death drill in a genuinely fresh runtime.
7. Run final exact-candidate gauntlet.
8. Only then qualify a simple durable accepted-event writer; until that gate passes, do not advance event watermark from canonical state.

## Cold-agent rule

This handoff accelerates recovery but never authorizes writes. A successor must verify live truth first.
