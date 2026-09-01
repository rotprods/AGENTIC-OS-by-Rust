# CP13 Assurance + Property + Operator Evidence — 2026-09-01

Authority: evidence projection. Live GitHub Actions and machine state/checkpoint outrank this file.

Semantic candidate: `b95de9444c6c33ba7296db56f416a293a39d6a3a`.

PASS set: Continuity `33454706427`; Rust `33454706438`; Parity `33454706435`; Property Union `33454706439`; Operator CLI `33454706462`; Supply Chain `33454706523`.

Supply-chain artifact ID `9781111361`, ZIP digest `sha256:891184ffb848fb6b0b640c6bcba96afe1447100f24275e4eb9de6170c639db56`. Machine qualification binds exactly to the candidate/run and reports identities, locked runtime, Python tools/audit, Rust tools/audit, TypeScript audit, Rust SBOM generation and Rust SBOM validation all `success`; nine Rust CycloneDX 1.5 documents are present.

Lock identities: Cargo `sha256:03b42bf650a8f52960ce8a92bc9f36848b215640ab58f4c673b09ddf5f05f370`; pnpm `sha256:80891079f6c2c0ce556e23910eb5e1435c2d1c424251f88ff0e0ef51f986a9f6`; Python CI `sha256:f40478d5ef14a29b48d06d7457721598856a46dade83978780107a4e9a9eb33f`; Python audit `sha256:82b787e4597a79dfe2444d1763647a3b6a1e1b4b343b9a168261a0e290357d88`.

Property union adds exact durable-prefix recovery, duplicate-event idempotency after reseal, rejected-append atomicity and repeated takeover fencing monotonicity without duplicating CP12.

Operator CLI verified read-only: `status`, `doctor`, `context`. `init`, `claim`, `checkpoint`, `handoff`, `recover` remain fail-closed. No network/process I/O or writer/recovery authority is granted.

Authority boundary: empirical NOT_RUN; CP01/02/03 BLOCKED_EXTERNAL; accepted-event writer UNQUALIFIED; watermark 0; network/process executors UNVERIFIED; multi-host DEFERRED; whole system IMPLEMENTED / SHADOW_ONLY.

Persistence changes the branch SHA. Requalify all six permanent gates on the persistence SHA and record final exact-head evidence externally on PR #4.
