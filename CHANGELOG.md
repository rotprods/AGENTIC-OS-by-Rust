# CHANGELOG

Canonical machine state/checkpoints and live exact-SHA CI outrank this projection.

## 2026-09-01 — CP13 Assurance + Property + Operator
- closed T17 supply-chain assurance with exact Cargo/pnpm/Python locks, pinned runtimes/actions, vulnerability audits and Rust/Python CycloneDX evidence;
- security-triggered Rust upgrade to 1.88.0 and `time 0.3.47` to remove `RUSTSEC-2026-0009`;
- direct TypeScript `ajv` upgraded to 8.18.0;
- added non-duplicative durable-store prefix/idempotency/atomicity/fencing properties;
- added Rust operator CLI read-only `status`, `doctor`, `context`;
- mutating/recovery CLI commands remain structured fail-closed;
- no event watermark or production authority promotion;
- CP01/CP02/CP03 and empirical fresh-successor hard gates remain open.

Earlier history is preserved in checkpoints, evidence, PR history and git history.
