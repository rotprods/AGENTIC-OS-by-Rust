# CP17 checkpoint binding RCA — 2026-09-10

Status: `DEFECT REPRODUCED / ROOT CAUSE PROVEN / REPAIR IN PROGRESS`
Authority: evidence only. This document does not repair, promote, or rewrite the malformed historical checkpoint.

## BUG

The persisted CP17 latest checkpoint
`rot://checkpoint/agentic-os/cp17-node24-actions-provenance-20260910`
failed the repository's fail-closed latest-checkpoint binding verifier even though its document integrity hash was valid.

Observed failure:

`verify_latest_checkpoint_binding -> verify_checkpoint -> checkpoint state binding mismatch`

The defect was first observed on PR #30 final persistence head
`92a43c13c6664b5b2b4c1c4d742a6d8e75589838` and reproduced on successor diagnostic heads.

## PHYSICAL EVIDENCE

Exact-checkout Continuity run:

- head: `441eb74e82bc739e3bc26d53a9bee51af5450480`
- workflow run: `34508524387`
- job: `102976560947`
- exact checkout: PASS
- Python tests: 177 executed; 176 PASS; one repository checkpoint-binding ERROR

Diagnostic values emitted by the clean runner:

- checkpoint `state_hash`: `sha256:8dae1f5f43a6a3e5d820b912fc12b2bef08be3cf7c539836192858d6d8d67262`
- durable current state with only `latest_checkpoint_id` rewound to the parent: `sha256:8dae1f5f43a6a3e5d820b912fc12b2bef08be3cf7c539836192858d6d8d67262`
- the same state after the canonical Survival V2 `_normalize_state` operation: `sha256:569eb151d9d2791de4e54f6e7dace80b0b5ae868fbe03a5d9b652eb1af68b167`

The only normalization delta was `decisions`:

- raw decisions hash: `sha256:a4b602a3340d7c3f97b88b96cfafcd293d12aadcb8dc22dd4a71aeafc872ee7a`
- normalized decisions hash: `sha256:57ce621f37b16c96fc44ef47fc2221c184093dcb391eafd2d48b2d00a2367a82`

No other state field changed under normalization.

## ROOT CAUSE

The historical CP17 checkpoint was sealed from the raw durable JSON representation rather than from the canonical normalized Survival V2 state representation used by `build_checkpoint` and required by `verify_checkpoint`.

The persisted raw state happened to contain a semantically set-like `decisions` collection in non-canonical order. The raw-state hash therefore differed from the canonical-state hash.

The verifier is behaving correctly. Weakening `verify_checkpoint` would convert a producer/procedure defect into silent acceptance of non-canonical checkpoint evidence.

## FAILURE FAMILY

This is not CP17-specific. The failure family is:

1. a producer manually constructs or reseals a checkpoint instead of calling the canonical builder; or
2. a producer hashes the raw JSON state while one or more set-like fields are unsorted or duplicated; or
3. a future producer and verifier use asymmetric normalization rules.

Affected set-like state fields include active workstreams, active claims, blockers, verified/unverified capabilities and decisions.

## INVARIANTS

1. `checkpoint.state_hash == hash_canonical(_normalize_state(sealed_state))`.
2. Raw JSON ordering of semantically set-like collections can never affect checkpoint identity.
3. Reordering or duplicating set-like state entries must not invalidate a checkpoint produced by `build_checkpoint`.
4. A checkpoint resealed with `hash_canonical(raw_state)` where raw and normalized states differ must fail closed.
5. Historical malformed checkpoint evidence is never rewritten for cleanliness; recovery is represented by a later child checkpoint.
6. The verifier is never relaxed to accept a malformed producer path.

## REGRESSION TEST

Permanent regression:

`python/tests/test_checkpoint_builder_normalization_v2.py`

It proves both directions:

- the canonical builder binds the normalized state and remains valid across reordered set-like inputs;
- a document-integrity-valid checkpoint resealed with the raw state hash is rejected with `checkpoint state binding mismatch`.

The temporary diagnostic `python/tests/test_cp17_checkpoint_diagnostic.py` exists only to expose the live historical delta and must be removed before final exact-head qualification.

## REPAIR STRATEGY

Do not modify the historical malformed CP17 checkpoint.

Repair by:

1. reconcile the current durable state with portfolio `GOAL_DRAIN / CONVERGENCE_ONLY` from issue #29;
2. produce one new child repair checkpoint whose parent is the malformed CP17 checkpoint;
3. generate that child exclusively through `build_checkpoint` semantics against the exact durable pre-pointer state;
4. advance `latest_checkpoint_id` only after the child document is persisted;
5. remove temporary diagnostic instrumentation;
6. run Continuity + Rust + Parity + Supply + Property + CLI on one exact final head;
7. only then consider expected-head/CAS integration of PR #30 into the current Survival branch.

## ADJACENT FAILURE FAMILY / GAUNTLET

The repair must additionally challenge:

- reordered decisions;
- duplicate decisions;
- reordered workstreams/blockers/capabilities;
- raw-state-hash resealing;
- pointer advance before checkpoint persistence;
- orphan parent;
- sibling fork;
- stale candidate head substitution.

Existing lineage/property/security tests already cover the latter four classes; the new normalization regression covers the escaped producer class.

## PORTFOLIO OVERRIDE

Issue #29 is fresher than the CP17 checkpoint's stale `CP18` next-action text.
After CP17 closes, the active mode is `GOAL_DRAIN -> CONVERGENCE_ONLY`: do not start CP18. Harvest and converge existing branches/PRs instead.
