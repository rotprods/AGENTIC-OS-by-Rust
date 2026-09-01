# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP14

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** It never outranks live GitHub, machine state/checkpoints, exact-SHA CI or revision-pinned governance evidence.

## Identity
- project: `rot://project/agentic-os`
- objective: `rot://objective/agentic-os/survival-v2-cp14-promotion-readiness`
- workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- checkpoint: `state/checkpoints/cp14-promotion-readiness-20260901.json`
- promotion branch/PR: `feat/graph-refactor-v2-survival` / #4, stacked on PR #1
- F1 semantic source: `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0`
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`

## CP14 semantic candidate evidence
`5baf4b2caddfe34e7499e9d0dce5f17b37fab322`

PASS: Continuity `33502307701`; Rust `33502307861`; Parity `33502307707`; Property `33502307734`; CLI `33502307901`; Supply Chain `33502307780`.

Promotion observer run `33502307722`, attempt 2: workflow `SUCCESS`, report `BLOCKED`.
Observed blockers are exactly:
- `HEAD_SIGNATURE_UNVERIFIED`
- `PROMOTION_ENFORCEMENT_MISSING`

Observed successful contexts include `assurance`, `continuity`, `durable-store-properties`, `operator-cli`, `parity`, `rust-contract-kernel`, plus the observer itself. The report observed no control-plane read error.

Supply artifact `9798323156`, digest `sha256:5ac3ad62c53437ae87589f841f6a594a0baa3a178cc008a5963541404e833e19`.
Observer artifact `9798348913`, digest `sha256:b9911b5bc6ebd8e1277c63cd4b4467b83165bf090c1161eae4aa019b354246c8`.

These runs become ancestor evidence after checkpoint persistence. Re-fetch all six required gates plus the observer on the final branch SHA. Because the observer can race the six required push checks, rerun its job on the same SHA after those checks close before treating its report as final.

## What changed
- Added a specification-only promotion policy containing the six real check contexts and required signed-head / PR / strict-check / no-force-push / no-deletion / admin controls.
- Added a stdlib-only live collector/evaluator and CLI producing `DERIVED_NON_AUTHORITATIVE` evidence.
- Added 8 deterministic fail-closed tests.
- Added a read-only pinned workflow with `actions/checks/contents: read`; no write permission is used.
- An adversarial diff review caught an initial collision with existing `python/rot_contracts/promotion.py`; that file was restored exactly and the observer moved to `promotion_readiness.py`.
- A live 403 on detailed branch protection was hardened without raising permissions: unprotected branches are recognized from branch metadata, while truly unreadable protected controls fail closed as `CONTROL_PLANE_UNOBSERVABLE`.
- PR #12 was integrated by non-force fast-forward.

## Empirical boundary
Verifier/schema/harness is VERIFIED. This session inherited predecessor context, so it did not qualify as a fresh independent successor and did not run/fabricate empirical evidence. Real empirical recovery remains `UNVERIFIED / NOT_RUN`.

## Governance boundary
`rot.knowledge/main` pinned `621550ddf725c0c3d1e41540ee878be124dfe871`; COS2 pinned `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`; CP01/CP02/CP03 remain `UNRESOLVED / BLOCKED_EXTERNAL`. Owner-wide literal and semantic searches did not identify a unique revision-pinned authority; never infer locators from names or similarity.

## GitHub promotion boundary
Canonical branch currently reports `protected=false`, required status-check enforcement `off`, no applicable repository ruleset, and unsigned/unverified head commits. The available connector has read access to those surfaces but exposes no compatible write action to configure enforcement. The observer therefore correctly remains `BLOCKED`; workflow success is not promotion authority.

## Hard blockers
1. CP01/CP02/CP03 authoritative locators.
2. Real independent empirical zero-context successor run.
3. GitHub promotion enforcement.
4. Signed/verified canonical head.
5. Durable accepted-event authority; watermark stays 0.

## Resume recipe
1. Read machine state and dynamically resolve `latest_checkpoint_id`.
2. Re-fetch PR #4 head/base and open topology before mutation.
3. Reject ancestor CI; require Continuity + Rust + Parity + Supply Chain + Property + CLI on the same current SHA.
4. After those six close, run/re-run Promotion Control Plane Readiness on that exact SHA and inspect JSON `ready/status/blockers`.
5. Retain `BLOCKED` while signature or GitHub enforcement blockers remain; never infer authority from observer workflow success.
6. Keep watermark 0, Survival SHADOW_ONLY, network/process executors UNVERIFIED and distributed authority DEFERRED.
7. Do not run empirical from a context-inheriting runtime and do not guess CP01/02/03.
8. Only after GitHub promotion + empirical + governance gates close should the final exact-candidate gauntlet precede durable writer qualification.
