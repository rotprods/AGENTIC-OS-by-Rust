# TASKS — Agent Survival V2

Authority: planning projection. Live PR/branch topology, `state/project_state.json`, latest checkpoint and exact-SHA executed CI outrank stale task prose.

## Current mode
`CP17_ATOMIC_CLOSE -> GOAL_DRAIN -> CONVERGENCE_ONLY`

Issue #29 supersedes the historical CP18 expansion plan. **Do not start CP18.**

## CP17 retained work
- [x] **SV2-001 — Exact-head runtime qualification infrastructure** — PR workflows explicitly execute `CANDIDATE_SHA`; synthetic merge refs are non-authority.
- [x] **SV2-003 — Rust/TS/Python behavioral parity reference**.
- [x] **SV2-004R — Reference accepted-event store** — production authority remains unqualified.
- [x] **SV2-005R — COS one-way projection adapter**.
- [x] **SV2-006R — Claims/fencing coordination reference**.
- [x] **SV2-007R — ContextPack compiler/invalidation reference**.
- [ ] **SV2-008 — Empirical death drill HARD GATE** — must come from a genuinely fresh independent runtime.
- [ ] **SV2-009 — Security/promotion gauntlet HARD GATE** — reference coverage exists; external promotion/signing and empirical recovery remain open.
- [ ] **SV2-010 — Operator UX PARTIAL** — read-only commands only; mutators intentionally unqualified.
- [x] **SV2-011 — T17 supply-chain provenance** — Node24-native exact Action SHAs, Ubuntu 24.04, hash-locked Python closure, frozen pnpm, exact executed-head evidence.
- [ ] **SV2-012 — External governance manifest** — candidate locators resolved; promotion blocked.
- [ ] **SV2-013 — Durable accepted-event authority** — watermark `0`; hard-gated.
- [x] **SV2-014 — Checkpoint continuity verifier/lineage**.
- [x] **SV2-015 — Survival child-lane core gates**.
- [x] **SV2-016 — Consumed-transition replay rule**.
- [x] **SV2-017 — Executed-source CI authority**.

## CP17 escaped defect wave
- [x] reproduce final-persistence Continuity failure on exact checkout;
- [x] prove historical CP17 `state_hash` was raw-state hash rather than canonical normalized-state hash;
- [x] isolate normalization delta to set-like `decisions`;
- [x] keep verifier fail-closed; do not weaken contract;
- [x] add permanent `test_checkpoint_builder_normalization_v2.py` regression;
- [x] persist `CP17_CHECKPOINT_BINDING_RCA_2026-09-10.md` with BUG / ROOT_CAUSE / FAILURE_FAMILY / INVARIANT / EVIDENCE;
- [x] canonicalize durable set-like state ordering;
- [x] replace stale CP18 next-action state with `GOAL_DRAIN / CONVERGENCE_ONLY`;
- [x] attach child checkpoint `cp17-continuity-repair-goal-drain-20260910` without rewriting malformed historical CP17 evidence;
- [x] advance latest-checkpoint pointer only after child persistence;
- [x] prove latest-checkpoint binding + new permanent regressions pass after pointer advance;
- [x] remove temporary diagnostic test;
- [ ] update remaining human projections/PR metadata to the repaired GOAL_DRAIN state;
- [ ] freeze one exact final PR #30 head;
- [ ] require Continuity + Rust + Parity + Supply + Property + CLI all SUCCESS on that exact head;
- [ ] perform adversarial exact-head review and live base/head preflight;
- [ ] if safe, integrate PR #30 into `feat/graph-refactor-v2-survival` with expected-head/CAS semantics;
- [ ] verify resulting canonical Survival branch head and post-integration workflows;
- [ ] persist terminal CP17 integration evidence/handoff.

## CP17 evidence
Implementation ancestor `ee695f8e14538faf1b354a637891f80cb0cd98c0` passed:
- Continuity `34503887361`
- Rust `34503887335`
- Parity `34503887336`
- Supply `34503887274`
- Property `34503887429`
- CLI `34503887378`

Escaped checkpoint defect reproduction:
- exact head `441eb74e82bc739e3bc26d53a9bee51af5450480`
- Continuity run `34508524387`
- job `102976560947`
- raw/pre-pointer hash `sha256:8dae1f5f43a6a3e5d820b912fc12b2bef08be3cf7c539836192858d6d8d67262`
- normalized hash `sha256:569eb151d9d2791de4e54f6e7dace80b0b5ae868fbe03a5d9b652eb1af68b167`
- only `decisions` changed under normalization.

Repair-pointer head `3d77c29fb711137bdd43ccab786e91533f858d28` proved the latest repair checkpoint binding and both permanent normalization regressions pass; its only Continuity failure came from the now-deleted temporary diagnostic asserting the old checkpoint was still latest. This is intermediate repair evidence, not final qualification.

## Post-CP17 convergence queue
Do not create feature waves from this queue. First classify existing live work.

1. Enumerate all remaining open PRs/branches in AGENTIC-OS-by-Rust, especially Survival/GGEV2 #4/#18/#19/#20 and adjacent assurance lanes.
2. For each, classify exactly one of: `PROMOTE_CANDIDATE`, `DONOR_PORT`, `SUPERSEDED`, `EVIDENCE_ONLY`, `SALVAGE_REBASE`, `BLOCKED_EXTERNAL`.
3. Diff stale/stacked lanes for unique invariants/tests/evidence before closure or supersession.
4. Port only unique value into the surviving canonical lineage; do not create parallel authorities.
5. Close or merge only after exact-head evidence and semantic ownership are reconciled. Never merge merely to reduce PR count.
6. Continue the same process repo-by-repo until the portfolio approaches `OPEN_PRS=0` through genuine convergence.

## External blockers that convergence cannot fake away
- CP01/CP02/CP03 promotion governance.
- GitHub required-check, PR-only, no-force-push, no-deletion/admin and signed-head enforcement.
- Genuine independent empirical zero-context recovery drill.
- Durable accepted-event production authority.
- Real network/process executor and multi-host authority qualification.

Lifecycle rule: PR #30 OPEN means candidate-only; MERGED means transition consumed; head/base drift means requalification. Every lifecycle decision starts with a live fetch.
