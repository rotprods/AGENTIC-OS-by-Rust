# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + machine-readable state/checkpoints + exact-SHA CI + revision-pinned governance evidence outrank this file when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / CP15_GOVERNANCE_CANDIDATE_RESOLUTION`

## Canonical topology
- PR #1: F1 base authority `015abe49353f744269d10cec7f7d3778a46e963c`.
- PR #4: sole Survival V2 promotion route, branch `feat/graph-refactor-v2-survival`.
- PR #13: CP15 governance-candidate lane; integrate only after final exact-head qualification.
- PR #14: isolated provenance probe only; merged on `probe/*` branches and did not modify canonical Survival.
- event watermark: `0`.
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`.

## CP15 semantic candidate
Candidate before continuity persistence: `91080a60f70bc9098dfd11bbd4e281345c9398ab`.

PASS on the same SHA:
- Store Property Union: `33513766213`
- Operator CLI Read-Only: `33513766240`
- CP13 Supply Chain Assurance: `33513766209`

Supply Chain completed the locked Rust/Python/TypeScript qualification, cargo-deny, pip-audit, pnpm high/critical audit, Rust/Python SBOM work and final enforcement gate.

Any persistence commit changes the branch SHA. The run IDs above are semantic-candidate evidence; final exact-head proof must be re-fetched after persistence and again after canonical integration.

## External governance resolution
`governance/external-authorities.v2.json` separates exact location from promotion authority.

- `rot.knowledge/main`: `6fcd62059f087c88454c555380c6eb37b7ad3ec2`, final `PINNED` repository-level constitutional/change-control reference after an eight-commit drift audit.
- ACM governance revision: `rotprods/rot.knowledge:feat/rot-life-graph-os-foundation@48b0d1eddb83b165237268c4334d6e19bbd969ec`.
- CP01: exact document located and `CANDIDATE_PINNED`; immutable runtime `649cc514...` independently passed GitHub-hosted `npm run ci`.
- CP02: exact document located and `CANDIDATE_PINNED`; canonical convergence runtime `07d94e9e...` passed `npm run deep:convergence` plus 20/20 flake runs. Parent `G-0001 CP-0300` compatibility and complete MID01 machine manifest/review remain open.
- CP03: exact document located and `CANDIDATE_PINNED`; SQLite reference runtime `1e30b4a0...` passed FAST + immutable deep qualification after a real independent run exposed and closed one typed JSON error-boundary defect. MID02/PostgreSQL/RLS/backend parity and independent security review remain open.
- COS2 remains pinned `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`.

`CANDIDATE_PINNED` is never promotion-qualified. Exact locator resolution closes the old `BLOCKED_EXTERNAL` discovery problem but does not authorize CP01/CP02/CP03 as production governance.

## GitHub signature path
Isolated PR #14 proved the native GitHub PR merge path can create a cryptographically verified commit:
`619e2a664257783e6a27d7db0e79eb5c93735ce2`, `verification.verified=true`, `reason=valid`, GitHub PGP signature.

This proves a signed integration mechanism. It does **not** provide branch/ruleset enforcement, signed-head enforcement, or promotion authority. CP15 should use this path with `expected_head_sha`, then the resulting canonical signature must be re-observed live.

## Hard blockers
1. Genuine fresh-runtime empirical zero-context successor drill.
2. CP01/CP02/CP03 promotion qualification; exact candidate locators are resolved but their own governance blockers remain.
3. GitHub required-check / PR / no-force-push / no-deletion / admin and signed-head enforcement.
4. Durable accepted-event writer qualification; watermark remains `0`.

## Authority ceiling
External governance candidate locators and the GitHub signed-merge path are verified evidence. Neither promotes the whole system. Empirical recovery remains `UNVERIFIED / NOT_RUN`; network/process executors are UNVERIFIED; durable accepted-event writer is UNQUALIFIED; multi-host authority is DEFERRED; whole Survival remains `IMPLEMENTED / SHADOW_ONLY`.

## Next safe frontier
Seal CP15, integrate it through the verified GitHub-native merge path, verify the resulting canonical signature, and rerun all required exact-head gates plus Promotion Control Plane Readiness. Then attack the remaining durable blockers: GitHub enforcement, CP governance promotion obligations, and the genuinely fresh empirical death drill. Do not qualify a durable writer or distributed infrastructure before those gates close.
