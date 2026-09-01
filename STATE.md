# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + machine-readable state/checkpoints + exact-SHA CI + revision-pinned governance evidence outrank this file when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / CP13_ASSURANCE_OPERATOR`

## Canonical topology
- PR #1: F1 base authority `015abe49353f744269d10cec7f7d3778a46e963c`.
- PR #4: sole active Survival V2 promotion route, branch `feat/graph-refactor-v2-survival`.
- PR #8/#10/#11: CP13 supply-chain/property/CLI lanes integrated by non-force fast-forward.
- event watermark: `0`.
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`.

## CP13 semantic candidate
Pre-persistence candidate: `b95de9444c6c33ba7296db56f416a293a39d6a3a`.

PASS: Continuity `33454706427`; Rust `33454706438`; Parity `33454706435`; Property Union `33454706439`; Operator CLI `33454706462`; Supply Chain `33454706523`.

Supply-chain artifact `9781111361`, digest `sha256:891184ffb848fb6b0b640c6bcba96afe1447100f24275e4eb9de6170c639db56`, reports 9/9 checks success and contains nine Rust CycloneDX 1.5 SBOMs.

Any persistence commit changes the branch SHA. The run IDs above are semantic-candidate evidence only; final exact-head qualification must be re-fetched live and recorded externally on PR #4 so evidence does not invalidate itself.

## CP13 completed assurance
- Rust runtime/MSRV moved to 1.88.0 because patched `time 0.3.47` requires it; `RUSTSEC-2026-0009` is removed.
- direct TypeScript `ajv` is 8.18.0.
- Cargo, pnpm and Python CI/audit dependency graphs are exact/hash-bound.
- Actions are exact-SHA pinned.
- cargo-deny, pip-audit, pnpm audit/dependency/license evidence and Rust/Python CycloneDX execute in CI.
- native pnpm CycloneDX remains deliberately deferred rather than forcing a pnpm major upgrade solely for SBOM generation.
- deterministic durable-store properties add prefix recovery, duplicate idempotency, rejected-append atomicity and repeated takeover fencing.
- Rust CLI read-only commands: `status`, `doctor`, `context`; all derived/non-authoritative.
- Rust CLI mutating/recovery commands: `init`, `claim`, `checkpoint`, `handoff`, `recover`; all intentionally fail closed until authority exists.

## Hard blockers
1. Genuine fresh-runtime empirical zero-context successor drill.
2. CP01/CP02/CP03 authoritative governance locators.
3. Durable accepted-event writer qualification; watermark remains `0`.
4. Repository-level required-check/signing enforcement before production promotion where permissions permit.

## Authority ceiling
Empirical verifier/schema is VERIFIED; real fresh successor is `UNVERIFIED / NOT_RUN`; network/process executors are UNVERIFIED; durable accepted-event writer is UNQUALIFIED; multi-host authority is DEFERRED; whole Survival remains `IMPLEMENTED / SHADOW_ONLY`.

## Next safe frontier
Resolve external governance only from unique revision-pinned evidence and run the empirical drill only in a genuinely fresh independent runtime. After both hard gates close, execute the final exact-candidate gauntlet and only then qualify a simple single-host durable accepted-event writer. Do not add distributed infrastructure without a measured trigger.
