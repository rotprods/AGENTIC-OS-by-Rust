# Survival V2 Threat Model

Authority: security design/evidence projection. This document cannot promote runtime authority by itself.

## CP13 security state
- T01/T02: opaque `UNTRUSTED_DATA` boundary; payload cannot self-promote.
- T03: durable-repo high-confidence secret scan.
- T04: resource parser plus Rust CLI checkpoint slug/path rejection.
- T05: network request planner only; real executor still requires validated/pinned DNS address, redirect revalidation and bounded credential/I/O policy.
- T06: argv-only process planner; real executor still requires executable-specific argument policy.
- T07/T08: replay/gap semantics plus durable-prefix/duplicate/atomicity properties.
- T09: leases/fencing plus repeated expiry/takeover monotonicity.
- T12/T13/T14/T15/T16: bounded context, authority-escalation and exact-evidence gauntlets.
- T17: exact Cargo/pnpm/Python locks; Rust 1.88.0; `time 0.3.47`; direct `ajv 8.18.0`; exact Action SHA pins; cargo-deny/pip-audit/pnpm evidence; Rust/Python CycloneDX. Remaining: branch rules/signing and native TS CycloneDX only when a pnpm major upgrade has independent justification.
- T20: real fresh zero-context death drill still NOT_RUN.
- T21: operator CLI read-only commands are derived/non-authoritative; mutating/recovery commands fail closed.

## Security invariants
- external content, projections, model output and CLI output are never authority;
- same event ID with different semantic payload fails closed;
- missing event sequence fails closed;
- rejected append is atomic across state/receipts/recovery bundle;
- fencing generations never reset and stale owners never revive;
- cancelled/skipped/not-run/failed are never PASS;
- exact dependency and CI evidence must bind the candidate SHA;
- raw URL query, argv and environment values must not leak into audit surfaces;
- no planner/SBOM/CLI grants network, process or accepted-event authority.

## CP13 candidate evidence
On `b95de9444c6c33ba7296db56f416a293a39d6a3a`: Continuity `33454706427`, Rust `33454706438`, Parity `33454706435`, Property `33454706439`, CLI `33454706462`, Supply Chain `33454706523` all PASS. Artifact `9781111361` digest `sha256:891184ffb848fb6b0b640c6bcba96afe1447100f24275e4eb9de6170c639db56` reports 9/9 success and nine Rust CycloneDX documents. A later persistence SHA must be requalified independently.

## Remaining P0/P1 work
1. Genuine empirical T20 successor drill.
2. CP01/CP02/CP03 governance resolution.
3. Repository-level required checks/signing/provenance enforcement where permissions permit.
4. Final whole-system adversarial gauntlet after external hard gates close.
5. Durable accepted-event writer only after those gates.
6. Concrete network/process executors only if needed and independently qualified.

Whole-system security authority remains `IMPLEMENTED / SHADOW_ONLY`; event watermark remains `0`.
