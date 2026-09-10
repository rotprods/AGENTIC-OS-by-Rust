# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + machine-readable state/checkpoints + exact-SHA CI + revision-pinned governance evidence outrank this file when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / CP16_POST_INTEGRATION_CONTINUITY_RECONCILIATION`

Whole-system authority remains `IMPLEMENTED / SHADOW_ONLY`. Event watermark remains `0`.

## Canonical topology
- PR #1: F1 base authority `015abe49353f744269d10cec7f7d3778a46e963c`.
- PR #4: sole Survival V2 promotion route, branch `feat/graph-refactor-v2-survival`.
- CP15 is **already integrated** into PR #4 at GitHub-verified merge commit `d19009055fb86e33836706fd0f09991869311431`. That transition is CONSUMED and must never be replayed from stale instructions.
- PR #28: isolated CP16 continuity-reconciliation lane based on exact CP15 head `d19009055...`. Its merge/integration lifecycle is external GitHub state and must always be re-read live; it is intentionally not encoded as an unconditional `next_safe_action`.
- Downstream GGEV2 PR #18 was reconstructed as based on `d19009055...`; if canonical Survival moves beyond that SHA, its derived snapshot is stale/rebuild-required before semantic integration.

## CP16 continuity defects closed in the candidate lane
1. **Consumed-transition replay defect** — CP15 had already been integrated while `STATE.md`, `TASKS.md`, `HANDOFF.md` and `state/project_state.json.next_safe_actions` still instructed a successor to integrate it. Canonical live projections now classify CP15 integration as consumed.
2. **Child-lane CI asymmetry** — Supply/Property/CLI ran on PRs targeting Survival, while Continuity/Rust/Parity did not. Those three core workflows now also trigger for PRs whose base is `feat/graph-refactor-v2-survival`.
3. **Checkpoint lineage ambiguity** — the latest checkpoint remains strict URI->canonical-path authority, while immutable legacy ancestors are structurally indexed only by unique internal checkpoint ID from the bounded `state/checkpoints/` directory. This preserves CP5's pre-convention filename and CP11 failed-construction evidence without allowing either to become current path authority.
4. **Stale ContextPack checkpoint boundary** — a checkpoint-pointer change alters the Survival projection/state seal and therefore invalidates an older ContextPack even when source SHA and event watermark are unchanged.

## Latest-checkpoint authority model
For current checkpoint `C`:

`state.latest_checkpoint_id = C`
-> resolve only `state/checkpoints/<canonical-C-slug>.json`
-> require `checkpoint.checkpoint_id == state.latest_checkpoint_id`
-> schema/hash validation
-> reconstruct the immediately pre-pointer state by setting only `latest_checkpoint_id = C.parent_checkpoint_id`
-> verify `C.state_hash` against that state.

Only the pointer transition is normalized. Drift in blockers, authority, watermark, verified capabilities, source SHA, claims, workstreams or next actions invalidates the binding.

Historical lineage verification is structural, not a retrospective authority promotion. CP11 remains intentionally preserved as failed-construction evidence and is not silently recertified.

## CP16 adversarial classification
- duplicate checkpoint ID / same ID different payload: DETECTABLE by unique-ID lineage indexing; latest payload tamper is also cryptographically rejected.
- self-parent and parent cycles: DETECTABLE.
- orphan parent: DETECTABLE.
- sibling concurrent checkpoints/fork: DETECTABLE when both artifacts coexist in the candidate tree.
- checkpoint file exists while state pointer remains on parent: DETECTABLE as pointer-behind partial write.
- state pointer advances while checkpoint file is absent: DETECTABLE as missing checkpoint partial write.
- rollback to an older checkpoint with otherwise newer state: DETECTABLE by state binding and, for legacy aliases, strict latest path resolution.
- stale ContextPack carrying an older checkpoint pointer: DETECTABLE by projection/state freshness seals.
- a semantically 'future' parent that is otherwise a valid acyclic existing ID has no trustworthy temporal meaning in the current checkpoint-ID contract: RESIDUAL / future schema or durable-writer responsibility.
- complete repository+state rollback to a self-consistent historical snapshot cannot be detected without an external monotonic authority/control plane: RESIDUAL / durable-writer + external enforcement responsibility.
- recovery from partial writes is currently operator/manual fail-closed recovery; it is not evidence of a qualified durable checkpoint writer.

## Governance truth
`governance/external-authorities.v2.json` remains the governance manifest.

- `rot.knowledge/main`: signed repository-level constitutional/change-control pin `afe43178ae492980ad0dead1b727b3092cfc5a13` as last reconstructed by CP15; **VERIFY LIVE BEFORE USE**.
- ACM governance revision: `rotprods/rot.knowledge:feat/rot-life-graph-os-foundation@48b0d1eddb83b165237268c4334d6e19bbd969ec`; **VERIFY LIVE BEFORE USE**.
- CP01/CP02/CP03: exact candidate locators exist, but all remain `CANDIDATE_PINNED`, not promotion authority.
- COS2 pin `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`; **VERIFY LIVE BEFORE USE**.

Exact locator resolution never equals governance promotion.

## GitHub signing/enforcement boundary
The isolated native-merge probe previously demonstrated that GitHub-native PR merge with `expected_head_sha` can produce a verified PGP-signed commit. That proves a usable signing path only. Required-check enforcement, PR-only writes, no-force-push, no-deletion, admin enforcement and signed-head enforcement remain external hard blockers until independently observed active.

## Empirical boundary
This CP16 session inherited predecessor context and **must not** claim a genuine fresh-successor death drill. Real empirical recovery remains `UNVERIFIED / NOT_RUN` unless raw independent evidence plus verifier result arrives from a separate fresh runtime.

## Hard blockers
1. Genuine fresh-runtime empirical zero-context successor drill.
2. CP01/CP02/CP03 promotion qualification beyond candidate locators.
3. GitHub required-check / PR / no-force-push / no-deletion / admin and signed-head enforcement.
4. Durable accepted-event writer qualification; watermark remains `0`.
5. Network/process executors and multi-host authority remain unqualified/deferred.

## Next safe frontier
1. Configure and independently observe the external GitHub promotion-enforcement controls and signed-head policy through an authorized control-plane write path.
2. Complete CP01/CP02/CP03 promotion governance without converting exact locator knowledge into authority.
3. Accept an empirical death-drill result only from a genuinely fresh independent runtime and verify its raw evidence contract.
4. After those hard gates close, run the final whole-system exact-candidate adversarial gauntlet.
5. Only then qualify a simple single-host durable accepted-event writer; keep watermark `0` until that qualification succeeds.

Lifecycle note: always fetch PR #28 live before acting. If it is already merged, the CP16 integration transition is consumed and must not be replayed. If it is still open, its candidate status does not grant authority by itself.
