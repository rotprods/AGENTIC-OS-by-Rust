# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP16

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** It never outranks live GitHub, machine state/checkpoints, exact-SHA CI or revision-pinned governance evidence.

## Identity
- project: `rot://project/agentic-os`
- objective: `rot://objective/agentic-os/survival-v2-cp16-post-integration-continuity-reconciliation`
- workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- expected latest checkpoint after CP16 seal: `state/checkpoints/cp16-post-integration-continuity-reconciliation-20260910.json`
- canonical Survival branch/PR: `feat/graph-refactor-v2-survival` / PR #4, stacked on PR #1
- CP16 candidate lane: `feat/cp16-post-integration-continuity-reconcile-20260910` / PR #28
- CP16 base reconstructed at creation: `d19009055fb86e33836706fd0f09991869311431`
- F1 semantic source: `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0`
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`

Every SHA/PR state above is **VERIFY LIVE BEFORE USE**.

## Consumed transition
CP15 is already integrated into canonical Survival at reconstructed GitHub-verified merge commit `d19009055fb86e33836706fd0f09991869311431`. The former instruction to integrate CP15 is stale and has been removed from the canonical successor surfaces. **Never replay CP15 integration.**

## CP16 result
The CP16 lane repairs three continuity-authority families:

1. Latest checkpoint is dynamically resolved; its ID/path/schema/document hash/state hash are verified. State binding seals the immediately pre-pointer state and rewinds only `latest_checkpoint_id` to the checkpoint parent, avoiding an impossible fixed point without ignoring unrelated state drift.
2. Checkpoint lineage topology detects duplicate IDs, cycles, self-parent, orphan parents, sibling forks, pointer-behind partial writes and pointer-ahead/missing-file writes. The selected latest path is always URI-derived. Immutable legacy ancestors are discovered only by scanning the bounded checkpoint directory and indexing unique internal IDs; this preserves CP5's historical filename alias and CP11 failed-construction evidence without granting either current path authority.
3. Child PRs targeting the Survival branch now execute Continuity + F1 Rust + F1 Parity pre-merge, closing the former asymmetry with Supply/Property/CLI.

A stale ContextPack carrying an older checkpoint pointer is also explicitly covered: the pointer change alters the projection/state seal and fails freshness validation.

## CP16 lifecycle — mandatory conditional handling
**Do not infer whether CP16 is integrated from this file. Fetch PR #28 and PR #4 live first.**

- If PR #28 is OPEN: CP16 is candidate-only. Compare its base with live PR #4 head and require the exact candidate head's applicable gates. Integration, if authorized, is an external GitHub lifecycle action and is deliberately not stored as an unconditional project `next_safe_action`.
- If PR #28 is MERGED: the integration transition is CONSUMED. Never attempt it again. Reconstruct the resulting PR #4 head/signature/check-runs and treat older candidate SHAs as ancestor evidence only.
- If PR #28 head/base changed, is closed unmerged, or conflicts with a moved Survival head: stop stale-write behavior, refresh, compare semantic deltas, preserve compatible work and rebuild/requalify as needed.

## Concurrency boundary
At CP16 reconstruction, GGEV2 PR #18 was based on Survival `d19009055...` and changed a disjoint GGEV2 file surface. If canonical Survival advances after CP16 integration, PR #18's exact-source-derived snapshot must be treated stale/rebuild-required before semantic integration. Do not force-overwrite it.

## Governance truth
Manifest remains `governance/external-authorities.v2.json`.

Last CP15 reconstructed pins — all **VERIFY LIVE BEFORE USE**:
- repository constitutional/change-control: `rot.knowledge/main@afe43178ae492980ad0dead1b727b3092cfc5a13`;
- ACM governance: `rotprods/rot.knowledge:feat/rot-life-graph-os-foundation@48b0d1eddb83b165237268c4334d6e19bbd969ec`;
- COS2: `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`.

CP01/CP02/CP03 remain `CANDIDATE_PINNED`, not final promotion authority. Exact location is not authority.

## Empirical boundary
This CP16 conversation inherited predecessor context. It is not a fresh independent successor and must not execute/self-attest the empirical death drill. Real empirical recovery remains `UNVERIFIED / NOT_RUN` unless raw evidence from a separate fresh runtime passes the existing verifier.

## Hard blockers
1. CP01/CP02/CP03 promotion governance remains open.
2. Real independent empirical zero-context successor run remains open.
3. GitHub required-check/PR/no-force-push/no-deletion/admin and signed-head enforcement remain open unless independently re-observed active.
4. Durable accepted-event authority remains unqualified; event watermark stays `0`.
5. Network/process executors and multi-host authority remain unqualified/deferred.

## Gauntlet residuals
- Complete self-consistent repository+state rollback is not detectable without an external monotonic authority/control plane.
- A valid acyclic parent ID has no trustworthy temporal ordering beyond explicit ancestry under the current ID contract; semantic future-parent prevention belongs to a future stronger checkpoint schema/durable writer.
- Partial-write defects are detectable but automated mutating recovery remains intentionally unqualified.

## Resume recipe
1. Fetch PR #4 and PR #28 live, including heads/bases/lifecycle. Then fetch all open competing PRs before mutation.
2. Read `state/project_state.json`; resolve `latest_checkpoint_id` dynamically; require the latest checkpoint at its canonical URI-derived path; verify schema, latest binding and lineage topology.
3. Read `STATE.md`, `TASKS.md`, this `HANDOFF.md`, CP16 evidence and the live exact-SHA check runs. If any contradict live GitHub/machine state, fail closed and reconcile.
4. Never execute a consumed integration transition. CP15 is already consumed; CP16 status is determined only from live PR #28 lifecycle.
5. Re-observe external governance revisions; drift fails closed. Never promote `CANDIDATE_PINNED` by naming similarity or prose.
6. Require Continuity + Rust + Parity + Supply + Property + CLI on the exact relevant candidate/canonical SHA; CANCELLED/SKIPPED/ancestor green is not final proof. Re-run/observe Promotion Control Plane Readiness on the same canonical candidate when promotion is evaluated.
7. Preserve event watermark `0`. Do not introduce durable writer, network/process executor or distributed authority before their explicit hard gates.
8. If canonical Survival advanced, refresh downstream GGEV2 exact-source snapshots before integrating them.
9. Highest-value safe work after CP16 is external GitHub enforcement, CP governance promotion obligations and independent empirical recovery; then final whole-system gauntlet, then durable writer qualification.
