# CHANGELOG

Canonical machine state/checkpoints and live exact-SHA CI outrank this projection.

## 2026-09-01 — CP15 External Governance Candidate Resolution
- located CP01/CP02/CP03 canonical governance documents at revision-pinned `rot.knowledge@48b0d1ed...`;
- introduced manifest v2 `CANDIDATE_PINNED` so exact location cannot be confused with promotion qualification;
- audited `rot.knowledge/main` from `621550dd...` to signed `6fcd6205...` across eight prompt-library commits, then re-audited a subsequent signed one-commit prompt-only advance to `afe43178...`; neither compare touched ACM governance, and the current repository-level pin is `afe43178...`;
- reconciled independent CP01 GitHub runner PASS, CP02 canonical `deep:convergence` + 20/20 flake PASS, and CP03 SQLite deep PASS while preserving remaining governance blockers;
- fixed stale governance test fixtures after ACM governance reconciliation;
- CP15 semantic candidate `91080a60...` passed Property `33513766213`, CLI `33513766240` and Supply Chain `33513766209`;
- CP15 persistence smoke subsequently caught a missing serialized checkpoint identity; corrected without changing runtime semantics;
- isolated PR #14 proved the GitHub-native merge endpoint produces a cryptographically verified PGP-signed merge commit (`619e2a66...`) without touching canonical Survival;
- no CP01/CP02/CP03, empirical, accepted-event writer, network/process or distributed authority promotion; watermark remains `0`.

## 2026-09-01 — CP14 Promotion Readiness
- added a machine-readable, specification-only promotion control-plane policy using the six real exact-head check contexts;
- added a stdlib-only live GitHub readiness observer and deterministic fail-closed tests;
- canonical semantic candidate passed all six required gates;
- observer remained BLOCKED by missing enforcement/signature conditions;
- no event watermark, empirical, writer, network/process or distributed authority promotion.

## 2026-09-01 — CP13 Assurance + Property + Operator
- closed T17 supply-chain assurance with exact Cargo/pnpm/Python locks, pinned runtimes/actions, vulnerability audits and Rust/Python CycloneDX evidence;
- security-triggered Rust upgrade to 1.88.0 and `time 0.3.47` to remove `RUSTSEC-2026-0009`;
- direct TypeScript `ajv` upgraded to 8.18.0;
- added non-duplicative durable-store prefix/idempotency/atomicity/fencing properties;
- added Rust operator CLI read-only `status`, `doctor`, `context`;
- mutating/recovery CLI commands remain structured fail-closed;
- no event watermark or production authority promotion.

Earlier history is preserved in checkpoints, evidence, PR history and git history.
