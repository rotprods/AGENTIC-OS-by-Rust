# CP16 — Post-Integration Continuity Authority Repair — 2026-09-10

Authority: durable evidence. This document records observations and invariants; it does not promote whole-system authority. Live GitHub lifecycle, `state/project_state.json`, the dynamically resolved latest checkpoint, exact-SHA CI and revision-pinned governance evidence outrank stale prose.

## Reconstructed starting truth
- Canonical Survival PR: #4, branch `feat/graph-refactor-v2-survival`.
- Reconstructed CP15 canonical head: `d19009055fb86e33836706fd0f09991869311431`, GitHub PGP-verified merge commit.
- F1 semantic base/source: `015abe49353f744269d10cec7f7d3778a46e963c`.
- CP15 latest checkpoint: `rot://checkpoint/agentic-os/cp15-governance-candidate-resolution-20260901`.
- Event watermark: `0`.
- Whole-system authority: `IMPLEMENTED / SHADOW_ONLY`.

All live values above must be re-fetched before future use.

## Discovery 1 — consumed-transition replay defect
The predecessor handoff described CP10->CP11 work, but live reconstruction showed CP15 already integrated. Despite that, `STATE.md`, `TASKS.md`, `HANDOFF.md` and `state/project_state.json.next_safe_actions` still instructed a successor to qualify/integrate CP15.

Failure family: **a lifecycle transition can succeed externally while durable successor guidance retains the pre-transition imperative**. A zero-context successor can therefore repeat or attempt to repeat a consumed transition.

Root invariant introduced:

`ConsumedIntegrationTransition --MUST_NOT_REMAIN--> CurrentNextSafeActions`

CP15 is now explicitly classified as consumed. PR #28 lifecycle is represented conditionally: fetch it live; OPEN means candidate-only, MERGED means consumed, drift means requalify. No unconditional self-merge instruction is stored in machine `next_safe_actions`.

Regression: `python/tests/test_post_integration_continuity_v2.py` rejects the escaped CP15 imperative family in canonical successor surfaces.

## Discovery 2 — Survival child-lane core CI asymmetry
Before CP16:
- Supply Chain, Property Union and Operator CLI workflows triggered on PRs targeting `feat/graph-refactor-v2-survival`.
- Continuity, F1 Rust and F1 Parity did not.

This allowed a child lane to be described as prequalified without running all three core gates until after canonical integration/push.

Repair:
- `.github/workflows/survival-v2-ci.yml` now includes Survival as a `pull_request` base.
- `.github/workflows/f1-rust-ci.yml` now includes Survival as a `pull_request` base.
- `.github/workflows/f1-parity-ci.yml` now includes Survival as a `pull_request` base.

The change was empirically exercised by PR #28: all six lane workflows were triggered. Regression: `test_survival_child_prs_execute_all_three_core_premerge_gates`.

## Checkpoint binding semantics — validated from first principles
`build_checkpoint(state S)` computes `state_hash = hash(normalize(S))`. Creating checkpoint `C` then changes only the canonical pointer from `C.parent_checkpoint_id` to `C.checkpoint_id`. Hashing the post-pointer state into C would require an impossible self-reference/fixed point.

Therefore the current invariant is:

```
CURRENT STATE
latest_checkpoint_id = C
        |
        v
resolve canonical C path
        |
        v
require C.checkpoint_id == state.latest_checkpoint_id
        |
        v
schema + checkpoint document hash
        |
        v
copy current state
set latest_checkpoint_id = C.parent_checkpoint_id   # ONLY normalized transition
        |
        v
verify C.state_hash against reconstructed pre-pointer state
```

No broad ignore list exists. Drift in blockers, authority, event watermark, verified capabilities, observed source SHA, active claims, active workstreams or next actions invalidates verification.

CP16 seal:
- checkpoint ID: `rot://checkpoint/agentic-os/cp16-post-integration-continuity-reconciliation-20260910`
- parent: CP15
- pre-pointer state hash: `sha256:102328600382912c9fa2c7b8209d49a29b0e95a7e45a5d1b0b9eebda5fa584c3`
- checkpoint document hash: `sha256:8a437822d1a273d7a5dd5709088e5334ae8ac2c006631ccaf1f9dc7b6cb19e41`

## Discovery 3 — legacy lineage path compatibility
The first new lineage test found a real historical compatibility fact:

- file: `state/checkpoints/cp5-survival-v2-20260829.json`
- internal identity: `rot://checkpoint/agentic-os/cp5-continuity-reference-20260830`
- CP6 correctly points to that internal identity.

This predates the current URI->filename naming invariant. Renaming/re-writing historical evidence would destroy continuity and broad path relaxation would weaken current authority.

Repair:
- the selected latest checkpoint is always required at its URI-derived canonical path;
- historical ancestors are discovered only by scanning the fixed bounded `state/checkpoints/` directory and indexing canonical internal IDs;
- IDs must be unique and parents are joined by ID, not path;
- a legacy alias cannot become latest because latest resolution remains strict;
- historical checkpoint payload hashes are not retrospectively promoted/re-certified; CP11 remains preserved failed-construction evidence.

## Discovery 4 — stale ContextPack failure channel
The explicit stale-checkpoint ContextPack test first expected a later `state hash` error, but the verifier correctly fails earlier at `stale projection`: `latest_checkpoint_id` participates in the state-derived projection hash.

The test was corrected to assert the actual earliest fail-closed boundary and also asserts that the projection hash changes. Runtime semantics were not weakened.

## Adversarial checkpoint gauntlet classification
| Attack / failure | Classification | Current mechanism / residual |
|---|---|---|
| duplicate checkpoint IDs | DETECTABLE | bounded directory scan + unique internal ID index |
| same ID / different payload | DETECTABLE | duplicate identity if both coexist; latest payload tamper also fails document hash |
| self-parent | DETECTABLE | parent-cycle detector |
| parent cycle | DETECTABLE | bounded ancestry + seen-set |
| orphan checkpoint parent | DETECTABLE | parent ID must resolve in bounded historical index |
| sibling concurrent checkpoints | DETECTABLE | fork detector on parent->children |
| checkpoint exists, pointer not advanced | DETECTABLE | `CHECKPOINT_POINTER_BEHIND` |
| pointer advanced, checkpoint absent | DETECTABLE | strict canonical latest resolver / `CHECKPOINT_NOT_FOUND` |
| wrong/tampered parent | DETECTABLE | document hash; if attacker reseals, pre-pointer state binding fails |
| rollback pointer with newer remaining state | DETECTABLE | state binding mismatch; legacy alias also cannot become latest path authority |
| stale ContextPack with old checkpoint pointer | DETECTABLE | projection/state freshness seal |
| malformed URI / traversal / wrong namespace | PREVENTED/DETECTABLE | canonical URI grammar + bounded canonical resolver |
| unrelated state drift | DETECTABLE | checkpoint state hash covers all normalized state fields |
| future-looking but existing acyclic parent | RESIDUAL | checkpoint IDs do not encode trusted wall-clock order; stronger schema/durable-writer semantics required |
| complete self-consistent repository+state rollback | RESIDUAL | requires external monotonic authority/control-plane protection |
| automatic mutating repair of partial write | DEFERRED | detection exists; durable checkpoint writer/recovery authority remains unqualified |

## Deterministic regression corpus added
`python/tests/test_latest_checkpoint_binding_v2.py` now covers:
- live repository latest binding;
- current lineage topology;
- sequential CP N -> pointer N -> CP N+1 -> pointer N+1 determinism;
- blocker drift;
- authority drift;
- event watermark drift;
- verified capability drift;
- observed source SHA drift;
- claim/workstream/next-action drift;
- checkpoint identity mismatch;
- parent tamper and resealed wrong-parent attack;
- payload/checkpoint-hash tamper;
- state-hash tamper with resealed document;
- rollback pointer;
- missing checkpoint;
- path traversal/wrong namespace/malformed checkpoint URI;
- self-parent/cycle/orphan/fork;
- both partial-write orders;
- duplicate ID/alias;
- strict latest filename binding.

`python/tests/test_context_pack_v2.py` explicitly covers stale checkpoint pointer invalidation.

## Candidate CI evidence before state/checkpoint persistence
Code candidate `784daf07ebe7f8b468b5e5d92c035bf25a94d8fd`:
- Survival V2 Continuity Gate `34500584020`: PASS.
- F1 Rust Contract Kernel `34500584425`: PASS.
- F1 Cross-Language Parity `34500583956`: PASS.
- Survival Store Property Union V2 `34500583973`: PASS.
- Survival Operator CLI Read-Only V1 `34500583978`: PASS.
- CP13 Supply Chain Assurance `34500584185`: CANCELLED after later CP16 persistence commits triggered concurrency cancellation. **CANCELLED is non-evidence.**

These are ancestor/candidate evidence only. They do not satisfy the final exact-head requirement after CP16 state/checkpoint/evidence persistence. The final exact-head run IDs must be read from live PR #28 metadata and are intentionally not embedded here because writing them would itself create a new head and invalidate exact-head identity.

## T17 runtime-deprecation observation
During CP16 Continuity logs, GitHub reported that the pinned `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` targets Node 20 and is being forced to Node 24 because Node 20 is deprecated on the hosted runner. The action remains commit-SHA pinned, so this is not an unpinned-action defect; it is a **runtime/provenance drift signal**. It must be re-audited against current upstream `actions/checkout` releases in the next T17 hardening wave rather than ignored or upgraded by guesswork.

## Authority boundaries preserved
- Event watermark remains `0`.
- Durable accepted-event writer remains unqualified.
- Real network/process executors remain unverified; only planner/validator boundaries exist.
- Multi-host authority remains deferred.
- CP01/CP02/CP03 remain candidate-pinned/promotion-blocked.
- This inherited-context session does not qualify the empirical death drill.
- No PostgreSQL/Redis/Kafka/Kubernetes/vector DB/GraphQL/production GraphRAG/MCP-A2A authority was introduced.

## Final exact-head acceptance rule
CP16 is not integration-qualified until the exact final PR #28 head has successful, non-cancelled runs for at least:
- Survival V2 Continuity Gate;
- F1 Rust Contract Kernel;
- F1 Cross-Language Parity;
- CP13 Supply Chain Assurance;
- Survival Store Property Union V2;
- Survival Operator CLI Read-Only V1.

After any canonical integration, re-fetch PR #4 exact head and repeat exact-head observation; ancestor green never counts.
