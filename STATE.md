# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + machine-readable state/checkpoints + exact-SHA CI + revision-pinned governance evidence outrank this file when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / CP14_PROMOTION_READINESS`

## Canonical topology
- PR #1: F1 base authority `015abe49353f744269d10cec7f7d3778a46e963c`.
- PR #4: sole active Survival V2 promotion route, branch `feat/graph-refactor-v2-survival`.
- PR #12: CP14 promotion-readiness lane integrated by non-force fast-forward.
- event watermark: `0`.
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`.

## CP14 semantic candidate
Pre-persistence candidate: `5baf4b2caddfe34e7499e9d0dce5f17b37fab322`.

PASS: Continuity `33502307701`; Rust `33502307861`; Parity `33502307707`; Property Union `33502307734`; Operator CLI `33502307901`; Supply Chain `33502307780`.

Promotion Control Plane Readiness run `33502307722`, attempt 2, also completed successfully on the same SHA after the six required checks closed. Its report is intentionally `BLOCKED`, not `READY`, with only:
- `HEAD_SIGNATURE_UNVERIFIED`
- `PROMOTION_ENFORCEMENT_MISSING`

The report observed all six required successful check contexts plus its own observer context, `branch_protected=false`, no applicable rulesets and no control-plane observability errors.

Supply-chain artifact `9798323156`, digest `sha256:5ac3ad62c53437ae87589f841f6a594a0baa3a178cc008a5963541404e833e19`.
Promotion-readiness artifact `9798348913`, digest `sha256:b9911b5bc6ebd8e1277c63cd4b4467b83165bf090c1161eae4aa019b354246c8`.

Any persistence commit changes the branch SHA. The run IDs above are semantic-candidate evidence only; final exact-head qualification must be re-fetched live and recorded externally on PR #4 so evidence does not invalidate itself.

## CP14 completed assurance
- Added `governance/promotion-control-plane.v1.json`, a policy specification that cannot grant promotion authority.
- Added a stdlib-only live observer for branch head, commit verification, exact-head checks, classic branch protection and repository rulesets.
- The observer fails closed on stale candidates, missing checks, unsigned heads, unreadable controls, bypass actors or incomplete enforcement.
- Existing `python/rot_contracts/promotion.py` was preserved byte-for-byte after adversarial review caught an initial namespace collision.
- No GitHub protection/ruleset write was performed; the available connector exposes no compatible configuration write action.
- Workflow token permissions remain read-only: `actions: read`, `checks: read`, `contents: read`, `metadata: read`.

## Hard blockers
1. Genuine fresh-runtime empirical zero-context successor drill.
2. CP01/CP02/CP03 authoritative governance locators.
3. Durable accepted-event writer qualification; watermark remains `0`.
4. GitHub required-check / PR / no-force-push / no-deletion / admin enforcement.
5. Cryptographically verified/signed canonical head.

## Authority ceiling
Promotion-readiness observer is `VERIFIED_REFERENCE / NON_AUTHORITATIVE`; its workflow success means only that observation executed. The live report remains `BLOCKED`. Empirical verifier/schema is VERIFIED; real fresh successor is `UNVERIFIED / NOT_RUN`; network/process executors are UNVERIFIED; durable accepted-event writer is UNQUALIFIED; multi-host authority is DEFERRED; whole Survival remains `IMPLEMENTED / SHADOW_ONLY`.

## Next safe frontier
Apply signed-head and repository promotion enforcement only through an authorized GitHub write path, then rerun the observer on the same exact candidate. Separately, resolve CP01/CP02/CP03 only from unique revision-pinned evidence and run the empirical drill only in a genuinely fresh independent runtime. Do not qualify the durable writer or add distributed infrastructure before those hard gates close.
