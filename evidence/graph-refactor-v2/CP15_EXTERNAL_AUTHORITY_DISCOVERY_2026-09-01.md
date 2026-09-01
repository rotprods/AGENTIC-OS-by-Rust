# CP15 External Authority Resolution & Independent Qualification — 2026-09-01

Authority: evidence projection only. Live GitHub, revision-pinned `rot.knowledge`, machine state/checkpoints and exact-SHA CI outrank this file.

## Result

CP01, CP02 and CP03 are no longer locator-unknown. CP15 now distinguishes three separate facts:

1. **locator exactness** — where the versioned governance candidate lives;
2. **independent qualification** — what immutable runtime candidate has actually executed on an independent GitHub-hosted runner;
3. **promotion authority** — whether parent governance has explicitly promoted that candidate.

The first two have advanced materially. The third remains fail-closed.

## Constitutional repository drift

The previous `rot.knowledge/main@621550ddf725c0c3d1e41540ee878be124dfe871` pin advanced by eight commits to signed HEAD:

`6fcd62059f087c88454c555380c6eb37b7ad3ec2`

The exact compare was reviewed before repinning. The observed delta is prompt-library/validation material and contains no `life-os-control` path change. GitHub reports the new main HEAD as cryptographically verified. The repository-level constitutional/change-control authority is therefore repinned to this SHA.

The canonical ACM governance branch was independently reconciled after new runner evidence and now stands at:

`rotprods/rot.knowledge / feat/rot-life-graph-os-foundation @ 48b0d1eddb83b165237268c4334d6e19bbd969ec`

That revision adds versioned independent-qualification addenda and a current qualification reconciliation state without promoting any checkpoint.

## CP01 — contract semantics reference

Canonical governance locator:
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- SHA: `48b0d1eddb83b165237268c4334d6e19bbd969ec`
- content: `life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP01_INDEPENDENT_GITHUB_QUALIFICATION_2026-09-01.md`

Runtime candidate:
- repository: `rotprods/mission-control`
- branch: `feat/acm-contract-kernel`
- SHA: `649cc51478844f62170600c4186ee0ffc221df0c`
- PR #2

The original GitHub-hosted runs on 2026-08-28 failed before checkout with no runner/steps. The same immutable candidate was re-executed on 2026-09-01:
- run `33173677622`
- successful rerun job `99857494321`
- checkout/runtime setup: PASS
- `npm run ci`: **PASS**

Therefore the old `INDEPENDENT_RUNNER_REQUIRED` execution blocker is closed. CP01 still remains `IN_PROGRESS / SHADOW_ONLY` until an explicit governance checkpoint transition/release decision.

## CP02 — canonical identity semantics

Canonical governance locator:
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- SHA: `48b0d1eddb83b165237268c4334d6e19bbd969ec`
- content: `life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP02_MID01_INDEPENDENT_DEEP_2026-09-01.md`

Canonical runtime candidate is **not** the old donor `feat/acm-identity-authority` branch. It is:
- repository: `rotprods/mission-control`
- branch: `feat/acm-cp02-convergence-mid01`
- current SHA: `07d94e9ec5b6e36515704e55d83178d1db276f3e`

The first real deep independent execution against predecessor `98ec375f...` passed functional convergence but failed the mandatory 100% line/function coverage threshold for shared canonical-JSON/hash helpers. No threshold was relaxed. A one-file test-only coverage patch produced current candidate `07d94e9...`.

Current candidate evidence:
- FAST run `33509487746`: **PASS**
- independent MID01 run `33509532612`, job `99861567852`: **PASS**
- `npm run deep:convergence`: **PASS**
- 20-run convergence flake campaign: **PASS**, divergence `0`
- clean candidate checkout after qualification: **PASS**

Exact candidate inspection and deep execution support closure of CP02 findings F001/F003/F004/F005/F006: opaque canonical IDs, workspace scope, transitive supersession cycle guard, generated resolver contract parity and independent runner execution are present/proven. F002 remains open for parent G-0001 CP-0300 compatibility/sign-off.

Formal `ACM-MID01` is **not auto-promoted**: the independent qualification packet requires one complete machine manifest with changed-line/generic-mutation/security/artifact fields. CP15 does not infer missing fields from the non-authoritative Drive mirror.

## CP03 — durable event-ledger semantics

Canonical governance locator:
- repository: `rotprods/rot.knowledge`
- ref: `feat/rot-life-graph-os-foundation`
- SHA: `48b0d1eddb83b165237268c4334d6e19bbd969ec`
- content: `life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP03_SQLITE_INDEPENDENT_QUALIFICATION_2026-09-01.md`

Current runtime candidate:
- repository: `rotprods/mission-control`
- branch: `feat/acm-cp03-sqlite-reference`
- SHA: `1e30b4a023513fae2f87de193b31de0dc1d89b6d`

The first real GitHub-hosted execution of predecessor `b91fe746...` executed 211 tests and found one real defect: malformed runtime JSON leaked a raw canonical-JSON `TypeError` instead of the public typed `INVALID_REQUEST` boundary. The candidate was fixed without changing SQLite/event semantics.

Current candidate evidence:
- FAST run `33509684541`, job `99862060259`: **PASS**
- immutable SQLite deep run `33509977149`, job `99863012530`: **PASS**
- candidate tree clean: **PASS**

The prior independent-execution blocker is closed for this SQLite reference candidate. Authority remains `SHADOW_ONLY`; `durable_event_authority=false`; SQLite remains `PERSISTENT_REFERENCE_NOT_GLOBAL_AUTHORITY`. MID02, PostgreSQL/RLS/backend parity, predecessor governance compatibility, independent architecture/security review and owner promotion remain open.

## Manifest model

`governance/external-authorities.v2.json` uses:

`CANDIDATE_PINNED`

Meaning:
- repository/ref/SHA/content locator is exact and freshness-checkable;
- explicit promotion blockers are mandatory;
- independent executable evidence may exist;
- it still never satisfies `assert_external_governance_ready`;
- only an explicit governance transition to final `PINNED`, with blockers cleared, can satisfy promotion.

This converts the CP01/02/03 problem from **unknown authority location** into **known exact, independently tested governance candidates whose promotion is still intentionally blocked**.

## Signing path probe

An isolated GitHub Contents API write on branch `probe/github-contents-signing-20260901` produced commit `40bf8eb8c2f10698ffd547cc4bb5d436e3367213` with `verification.verified=false`, `reason=unsigned`.

Separately, `rot.knowledge/main` demonstrates that native GitHub merge commits can be cryptographically verified. CP15 will therefore test the native GitHub merge path for the Survival integration rather than assuming Contents/Git Data writes can satisfy signed-head policy.
