# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP17

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** Live GitHub + `state/project_state.json` + dynamically resolved latest checkpoint + physically verified exact-SHA CI outrank this file.

## Identity
- project: `rot://project/agentic-os`
- objective: `rot://objective/agentic-os/survival-v2-cp17-continuity-repair-goal-drain`
- workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- latest checkpoint expected at this handoff: `rot://checkpoint/agentic-os/cp17-continuity-repair-goal-drain-20260910`
- checkpoint file: `state/checkpoints/cp17-continuity-repair-goal-drain-20260910.json`
- malformed historical parent retained as evidence: `rot://checkpoint/agentic-os/cp17-node24-actions-provenance-20260910`
- canonical Survival branch/PR: `feat/graph-refactor-v2-survival` / PR #4
- CP17 candidate lane: `feat/cp17-node24-actions-provenance-20260910` / PR #30
- CP17 base at creation: `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7`
- F1 semantic source: `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0`
- authority ceiling: `IMPLEMENTED / SHADOW_ONLY`
- portfolio execution mode: `GOAL_DRAIN / CONVERGENCE_ONLY` from issue #29

Every SHA and lifecycle state is **VERIFY LIVE BEFORE USE**.

## Mandatory successor reconstruction
1. Fetch issue #29, PR #30 and PR #4 live before any mutation.
2. Read `state/project_state.json`; resolve `latest_checkpoint_id` dynamically; verify latest checkpoint integrity, exact pre-pointer state binding and full lineage topology.
3. Read `STATE.md`, `TASKS.md`, this handoff and `evidence/graph-refactor-v2/CP17_CHECKPOINT_BINDING_RCA_2026-09-10.md`.
4. Require physical `git HEAD == CANDIDATE_SHA` for every PR qualification claim. PR run metadata `head_sha` alone is not executed-source authority.
5. Never rewrite the malformed historical CP17 checkpoint. Its failure is preserved evidence and superseded by the repair child.

## CP17 implementation retained
CP17 hardens T17 and executed-source authority without promoting runtime authority:
- audited exact Node24-native first-party Action pins;
- Ubuntu 24.04 permanent runners;
- Python 3.12.3 Continuity and Python 3.13.15 Parity provenance;
- frozen/hash-locked dependency closures;
- named + unnamed `uses:` Action inventory;
- `persist-credentials:false` checkout policy;
- explicit PR candidate checkout + physical HEAD assertion;
- CP13 evidence bound to executed `CANDIDATE_SHA`.

Pre-persistence code candidate `ee695f8e14538faf1b354a637891f80cb0cd98c0` passed:
- Continuity `34503887361`
- Rust `34503887335`
- Parity `34503887336`
- Supply `34503887274`
- Property `34503887429`
- CLI `34503887378`

These are ancestor evidence after persistence changes. They never substitute for final-head qualification.

## Escaped checkpoint defect
The first persisted CP17 checkpoint was document-integrity-valid but state-binding-invalid.

Exact physical reproduction:
- source head `441eb74e82bc739e3bc26d53a9bee51af5450480`
- Continuity run `34508524387`
- job `102976560947`
- historical checkpoint raw/pre-pointer state hash: `sha256:8dae1f5f43a6a3e5d820b912fc12b2bef08be3cf7c539836192858d6d8d67262`
- canonical normalized state hash: `sha256:569eb151d9d2791de4e54f6e7dace80b0b5ae868fbe03a5d9b652eb1af68b167`
- only normalization delta: set-like `decisions` ordering.

Root cause: historical checkpoint emission hashed raw durable JSON rather than canonical normalized state used by `build_checkpoint` and `verify_checkpoint`.

The verifier remains unchanged/fail-closed.

Permanent regression:
`python/tests/test_checkpoint_builder_normalization_v2.py`

RCA:
`evidence/graph-refactor-v2/CP17_CHECKPOINT_BINDING_RCA_2026-09-10.md`

## Repair transaction
The repair was performed as a forward-only succession, not history rewrite:

`durable state reconciled/canonicalized`
→ `child checkpoint persisted`
→ `latest_checkpoint_id advanced`
→ `binding verified`
→ `temporary diagnostic removed`.

Repair child:
`rot://checkpoint/agentic-os/cp17-continuity-repair-goal-drain-20260910`
parent:
`rot://checkpoint/agentic-os/cp17-node24-actions-provenance-20260910`.

On intermediate repair-pointer head `3d77c29fb711137bdd43ccab786e91533f858d28`, repository latest-checkpoint binding and both permanent normalization regressions passed. Its single Continuity failure was the deliberately temporary diagnostic asserting the old checkpoint was still latest; that diagnostic was removed in the next commit. Treat this as repair proof, not final qualification.

## Fresher portfolio override: no CP18
Historical CP17 state/handoff text that named CP18 as the next feature wave is superseded by issue #29.

After CP17 is safely integrated:

`GOAL_DRAIN -> CONVERGENCE_ONLY`

Required behavior:
- do not open CP18;
- enumerate surviving open branches/PRs;
- classify each as `PROMOTE_CANDIDATE`, `DONOR_PORT`, `SUPERSEDED`, `EVIDENCE_ONLY`, `SALVAGE_REBASE` or `BLOCKED_EXTERNAL`;
- harvest unique tests/invariants/evidence before closure;
- port unique value only into the surviving semantic owner;
- never blind-merge or close merely to achieve a smaller PR count;
- converge repo-by-repo toward `OPEN_PRS=0` as an outcome of semantic closure.

## Remaining CP17 atomic close
1. Finish current human-readable projection/PR metadata persistence.
2. Freeze one exact final PR #30 head.
3. Require all six current-head workflows SUCCESS: Continuity, Rust, Parity, Supply, Property, CLI.
4. Review any prior red as evidence; no retry-until-green masking.
5. Refresh PR #4 base/head and all overlapping claims immediately before integration.
6. Only if topology and exact-head qualification remain valid, integrate PR #30 into `feat/graph-refactor-v2-survival` using expected-head/CAS semantics.
7. Read back resulting Survival head and exact post-integration workflow evidence.
8. Persist terminal CP17 integration evidence and update next action to convergence inventory. Do not start CP18.

## External hard blockers that remain real
- CP01/CP02/CP03 promotion governance beyond candidate locators.
- required-check, PR-only, no-force-push, no-deletion/admin and signed-head enforcement not independently qualified.
- genuine fresh independent empirical zero-context death drill.
- durable accepted-event production writer.
- real network/process executor and multi-host authority.

Event watermark stays `0` until durable accepted-event authority is genuinely qualified.

## Stop-line
Stop mutation and reconstruct if:
- PR #30 head/base moves unexpectedly;
- PR #4 changes under the integration preflight;
- any exact-head gate is red/skipped/cancelled/not-run;
- a competing semantic writer appears;
- checkpoint/state lineage diverges;
- the portfolio GOAL_DRAIN override changes;
- integration would be interpreted as portfolio promotion rather than feature-branch convergence.
