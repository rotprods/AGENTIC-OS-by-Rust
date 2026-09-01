# CP15 External Authority Locator Resolution — 2026-09-01

Authority: evidence projection only. Live GitHub, revision-pinned `rot.knowledge`, machine state/checkpoints and exact-SHA CI outrank this file.

## Result

CP01, CP02 and CP03 are no longer locator-unknown.

The previously pinned `rot.knowledge/main@621550ddf725c0c3d1e41540ee878be124dfe871` had advanced by eight commits to `6fcd62059f087c88454c555380c6eb37b7ad3ec2`. The exact compare was reviewed before repinning: the delta is prompt-library/validator material and contains no `life-os-control` path change. GitHub reports the new main HEAD as cryptographically verified. CP15 therefore repins the repository-level constitutional/change-control authority to `6fcd62059f087c88454c555380c6eb37b7ad3ec2`; CP01/CP02/CP03 remain independently pinned to the governance candidate revision below.

The canonical CP governance surface is `rotprods/rot.knowledge`, branch `feat/rot-life-graph-os-foundation`, observed at exact SHA:

`94d62493e5347bc6767a5784e5cab597d7a79147`

The branch contains `life-os-control/subsystems/agentic-context-mesh/CHECKPOINT_REGISTRY.json`, which names:
- `ACM-CP01 — CONTRACT_KERNEL` as `IN_PROGRESS`;
- `ACM-CP02 — IDENTITY_AUTHORITY` as `OPEN`;
- `ACM-CP03 — EVENT_LEDGER` as `OPEN`;
and states that plans, documentation, code volume, test count or model confidence cannot promote a checkpoint without versioned executable evidence.

## Exact canonical locators

### CP01 — contract semantics reference
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- pinned governance SHA: `94d62493e5347bc6767a5784e5cab597d7a79147`
- content: `life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP01_HARDENING_ADDENDUM_2026-08-28.md`
- governance decision: `IN_PROGRESS / SHADOW_ONLY`
- mapped runtime: `rotprods/mission-control`, `feat/acm-contract-kernel@649cc51478844f62170600c4186ee0ffc221df0c`, PR #2
- blocker: independent exact-head runner evidence and parent promotion decision remain open.

### CP02 — canonical identity semantics
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- pinned governance SHA: `94d62493e5347bc6767a5784e5cab597d7a79147`
- content: `life-os-control/subsystems/agentic-context-mesh/CP02_CONVERGENCE_CANDIDATE_STATE.json`
- governance decision: `CANDIDATE_PUBLISHED_FORMAL_NO_GO / SHADOW_ONLY`
- runtime branch independently observed: `rotprods/mission-control`, `feat/acm-identity-authority@60c0bd68d587998564e3dc5a4f5516a134a35317`, live PR #17
- Git lineage: CP02 is `59` commits ahead and `0` behind CP01 head `649cc514...`; merge base is CP01.
- stale mirror finding: older Drive text naming mission-control PR #4 is not current topology; PR #4 has been repurposed and must not be used as CP02 lifecycle authority.

### CP03 — durable event ledger semantics
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- pinned governance SHA: `94d62493e5347bc6767a5784e5cab597d7a79147`
- content: `life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP03_SQLITE_REFERENCE_WAVE_2026-08-29.md`
- governance decision: `SHADOW_ONLY / NO_GO_EXTERNAL_AND_PREDECESSOR_GATES_OPEN`
- mapped runtime: `rotprods/mission-control`, `feat/acm-cp03-sqlite-reference@b91fe7468d3888c30209c704d2c4c66aa9075198`, PR #23
- runtime machine state explicitly says `durable_event_authority=false`, SQLite is `PERSISTENT_REFERENCE_NOT_GLOBAL_AUTHORITY`, PostgreSQL is disabled, and independent execution remains open.
- lineage: CP03 and the observed CP02 runtime are diverged; their common merge-base family is CP01. No CP02→CP03 ancestry is claimed.

## Model correction

The former manifest model allowed only `PINNED` or `UNRESOLVED`. That was insufficient once an exact locator was discovered for a candidate whose own governance explicitly denies promotion.

Schema v2 therefore introduces:

`CANDIDATE_PINNED`

Meaning:
- repository/ref/SHA/content locator is exact and can be freshness-checked;
- explicit promotion blockers are mandatory;
- it never satisfies `assert_external_governance_ready`;
- only an explicit governance transition to final `PINNED`, with blockers cleared and exact-head observation, can satisfy promotion.

This converts the CP01/CP02/CP03 problem from **unknown location** to **known exact candidate, intentionally not promotion-qualified** without weakening fail-closed behavior.

## Signing probe

An isolated GitHub Contents API probe on branch `probe/github-contents-signing-20260901` produced commit:

`40bf8eb8c2f10698ffd547cc4bb5d436e3367213`

GitHub reported `verification.verified=false`, `reason=unsigned`.

Therefore the available GitHub write paths in this runtime do not remove `HEAD_SIGNATURE_UNVERIFIED`. The probe is evidence-only and is not part of the Survival promotion branch.
