# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + `state/project_state.json` + dynamically resolved latest checkpoint + physically verified exact-checkout CI outrank this file when stale.

## Current phase
`CP17_CONTINUITY_REPAIR / GOAL_DRAIN / CONVERGENCE_ONLY`

Whole-system authority remains `IMPLEMENTED / SHADOW_ONLY`. Event watermark remains `0`.

Portfolio issue #29 is the current execution override: finish the already-claimed CP17 atomic transition, then **do not start CP18**. After CP17 integration, harvest and converge existing branches/PRs instead of expanding architecture.

## Canonical topology
- PR #1: F1 semantic/base authority source `015abe49353f744269d10cec7f7d3778a46e963c` — verify live before use.
- PR #4: sole Survival V2 integration route, branch `feat/graph-refactor-v2-survival`.
- CP16 canonical Survival head at CP17 branch creation: `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7` — verify live before integration.
- PR #30: isolated CP17 T17/provenance + continuity-repair candidate. Its current head must be fetched live before every lifecycle mutation.
- GGEV2 #18/#19/#20 remain downstream/derived lanes to classify after CP17 under GOAL_DRAIN; they must not be force-overwritten from stale Survival snapshots.

## CP17 implementation value already retained
1. First-party JS Actions use exact audited Node24-native release SHAs rather than Node20-targeting pins silently forced by hosted runners.
2. Permanent workflows pin Ubuntu 24.04.
3. F1 Parity pins Python 3.13.15 + hash-locked CI requirements, Node 24.20.0, pnpm 10.15.0 and frozen lock behavior.
4. Continuity pins Python 3.12.3 with isolated hash-locked dependency closure.
5. Action inventory parses named and unnamed YAML `uses:` forms.
6. PR qualification explicitly checks out `pull_request.head.sha || github.sha` and asserts physical `git HEAD == CANDIDATE_SHA`; synthetic `refs/pull/*/merge` metadata is not exact-head authority.
7. CP13 evidence binds to executed `CANDIDATE_SHA` rather than synthetic `GITHUB_SHA`.

Pre-persistence code candidate `ee695f8e14538faf1b354a637891f80cb0cd98c0` passed six explicit exact-checkout gates:
- Continuity `34503887361`
- Rust `34503887335`
- Parity `34503887336`
- Supply `34503887274`
- Property `34503887429`
- CLI `34503887378`

Those runs remain code-delta ancestor evidence only after persistence changes. Final PR #30 integration requires a fresh six-gate run on one exact final head.

## CP17 escaped continuity defect and repair
The original CP17 checkpoint `rot://checkpoint/agentic-os/cp17-node24-actions-provenance-20260910` is preserved as malformed historical evidence; it is **not** rewritten.

Physical exact-checkout Continuity run `34508524387` / job `102976560947` proved:
- stored historical checkpoint `state_hash` = `sha256:8dae1f5f43a6a3e5d820b912fc12b2bef08be3cf7c539836192858d6d8d67262`;
- raw durable pre-pointer state hash = the same value;
- canonical normalized state hash = `sha256:569eb151d9d2791de4e54f6e7dace80b0b5ae868fbe03a5d9b652eb1af68b167`;
- the only normalization delta was the set-like `decisions` collection.

Root cause: the checkpoint was emitted from raw JSON state instead of canonical `build_checkpoint` normalization semantics. The verifier was correct and remains unchanged.

Permanent regression: `python/tests/test_checkpoint_builder_normalization_v2.py`.

RCA: `evidence/graph-refactor-v2/CP17_CHECKPOINT_BINDING_RCA_2026-09-10.md`.

Repair checkpoint now attached as the latest child:
`rot://checkpoint/agentic-os/cp17-continuity-repair-goal-drain-20260910`
→ `state/checkpoints/cp17-continuity-repair-goal-drain-20260910.json`.

The child binds the exact canonical pre-pointer state and keeps the malformed predecessor in lineage as superseded evidence. On head `3d77c29fb711137bdd43ccab786e91533f858d28`, the repository latest-checkpoint binding test and the new permanent normalization regressions passed; the only Continuity failure was the temporary diagnostic deliberately expecting the old checkpoint to remain latest. That diagnostic has since been removed. This is repair evidence, not final-head qualification.

## Current hard blockers
1. Final PR #30 exact-head Continuity/Rust/Parity/Supply/Property/CLI qualification after all persistence/doc changes finish.
2. Expected-head/CAS integration into the then-live Survival branch; candidate green is not integration authority by itself.
3. Genuine fresh-runtime empirical zero-context successor drill.
4. CP01/CP02/CP03 promotion qualification beyond candidate locators.
5. GitHub required-check / PR-only / no-force-push / no-deletion / admin and signed-head enforcement independently active.
6. Durable accepted-event writer, real network/process executors and multi-host authority remain unqualified; watermark stays `0`.

## Next safe frontier
1. Finish CP17 durable projections/handoff, freeze one exact PR #30 head and require all six qualification gates green on that head.
2. If and only if the live Survival base still matches a safe integration boundary, integrate PR #30 using expected-head/CAS semantics and verify the resulting canonical Survival head + push CI.
3. **Do not open CP18.** Enter `GOAL_DRAIN / CONVERGENCE_ONLY`.
4. Enumerate remaining open Survival/GGEV2/adjacent PRs and classify each as `PROMOTE_CANDIDATE`, `DONOR_PORT`, `SUPERSEDED`, `EVIDENCE_ONLY`, `SALVAGE_REBASE` or `BLOCKED_EXTERNAL` before mutation.
5. Harvest unique invariants/evidence into the surviving lineage, then close/merge only when semantically justified. `OPEN_PRS=0` is an outcome of convergence, never a reason to blind-merge.

Lifecycle law: every SHA and PR state above is **VERIFY LIVE BEFORE USE**. If PR #30 is already merged, never replay integration. If its head/base moved, requalify. Green CI remains assurance evidence only while promotion enforcement/signing are unresolved.
