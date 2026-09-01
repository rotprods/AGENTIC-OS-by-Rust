# CP14 Promotion Control-Plane Readiness Evidence — 2026-09-01

Authority: evidence projection. Live GitHub Actions, machine state/checkpoint and external GitHub enforcement state outrank this file.

Semantic candidate: `5baf4b2caddfe34e7499e9d0dce5f17b37fab322`.

Required exact-head PASS set:
- Continuity `33502307701`
- Rust `33502307861`
- Cross-Language Parity `33502307707`
- Durable Store Property Union `33502307734`
- Operator CLI `33502307901`
- Supply Chain `33502307780`

Supply-chain artifact ID `9798323156`, digest `sha256:5ac3ad62c53437ae87589f841f6a594a0baa3a178cc008a5963541404e833e19`.

Promotion Control Plane Readiness run `33502307722` was re-run after the six required checks closed. Attempt 2 job `99839560236` completed `SUCCESS`; 8 deterministic observer tests passed.

Final live observer JSON at the semantic candidate:
- `authority = DERIVED_NON_AUTHORITATIVE`
- `promotion_authority = false`
- `ready = false`
- `status = BLOCKED`
- `HEAD_SIGNATURE_UNVERIFIED`
- `PROMOTION_ENFORCEMENT_MISSING`
- `branch_protected = false`
- `head_verified = false`
- `control_plane_errors = {}`
- no applicable active repository rulesets
- successful check contexts observed: `assurance`, `continuity`, `durable-store-properties`, `operator-cli`, `parity`, `rust-contract-kernel`, plus `promotion-control-plane-observer`.

Observer artifact ID `9798348913`, ZIP digest `sha256:b9911b5bc6ebd8e1277c63cd4b4467b83165bf090c1161eae4aa019b354246c8`.

The observer's GitHub token permissions were read-only: Actions read, Checks read, Contents read, Metadata read.

Adversarial fixes made before integration:
1. initial namespace collision with existing `python/rot_contracts/promotion.py` was detected from the PR diff; the original file was restored byte-for-byte and the new implementation moved to `promotion_readiness.py`;
2. detailed protection reads returned HTTP 403 under the read-only token; the collector was hardened to trust public branch metadata for `protected=false` and to fail closed as `CONTROL_PLANE_UNOBSERVABLE` whenever a protected control cannot actually be read.

PR #12 was integrated into the canonical Survival branch by non-force fast-forward. No branch-protection/ruleset write was performed because no compatible connector write action is exposed.

Authority boundary remains unchanged: empirical NOT_RUN; CP01/02/03 BLOCKED_EXTERNAL; accepted-event writer UNQUALIFIED; watermark 0; network/process executors UNVERIFIED; multi-host DEFERRED; whole system IMPLEMENTED / SHADOW_ONLY.

Persistence changes the branch SHA. Requalify all six required gates plus the observer on the persistence SHA. Run/re-run the observer only after the six required checks close, then record final exact-head evidence externally on PR #4.
