# TASKS — Agent Survival V2

Authority: planning projection. Task completion requires exact evidence and applicable state/graph/handoff updates.

## P0/P1 executable frontier

- [ ] **SV2-001 — Exact-head combined CI**
  - Depends on: PR #3 head frozen.
  - DoD: F1 Rust workflow SUCCESS; F1 parity workflow SUCCESS; Survival V2 Python/schema tests executed in that run; no cancelled/skipped job counted as PASS.

- [ ] **SV2-002 — Reconcile/supersede PR topology**
  - Depends on: SV2-001.
  - Action: prove PR #3 is superset of #1 + intended #2 coverage; only then mark #1/#2 SUPERSEDED or preserve any unique missing delta.
  - DoD: one canonical implementation branch/PR remains; historical PRs preserved, not rewritten.

- [ ] **SV2-003 — Survival Rust/TS/Python parity**
  - Depends on: schema freeze after SV2-001.
  - Outputs: continuity state/checkpoint/freshness/replay golden fixtures and implementations.
  - DoD: canonical bytes/hash/schema accept-reject parity 100%.

- [ ] **SV2-004 — Reference accepted-event store**
  - Depends on: SV2-003 contract semantics.
  - DoD: expected revision; idempotent duplicate; conflicting duplicate fails closed; watermark/snapshot/replay deterministic.

- [ ] **SV2-005 — COS one-way projection adapter**
  - Depends on: SV2-004.
  - DoD: event/state → typed graph; delete/rebuild gives same canonical hash; no reverse-write API.

- [ ] **SV2-006 — Claims/barriers conflict engine**
  - Depends on: SV2-004.
  - DoD: file/tree/semantic conflicts; stale ownership cannot authorize mutation; branch != ownership.

- [ ] **SV2-007 — ContextPack compiler/invalidation**
  - Depends on: SV2-005/SV2-006.
  - DoD: observed source/event/projection seal; upstream drift rejects write-capable pack.

- [ ] **SV2-008 — Agent death drill**
  - Depends on: SV2-004..007.
  - DoD: fresh zero-context agent reconstructs bounded state/ownership/evidence/blockers/next 3 safe actions <=5 minutes and <=1 pack.

- [ ] **SV2-009 — Continuity security gauntlet**
  - Attack prompt/provider poisoning, secrets/PII, path/URL/shell injection, stale writer, replay/evidence substitution, duplicate spend/operation, authority self-promotion.
  - DoD: P0/P1=0 or explicit BLOCKED.

- [ ] **SV2-010 — Bootstrap/install UX**
  - Depends on: contracts stable.
  - Output: `agentic-os init/status/context/claim/checkpoint/handoff/recover/doctor` design/implementation.
  - DoD: adoption is non-destructive and creates no competing authority.

## Deferred until measured trigger
- PostgreSQL durable backend;
- Redis/Kafka/queues;
- Kubernetes/multi-host workers;
- vector DB / GraphRAG runtime;
- GraphQL/MCP/A2A/Mission Control production surfaces.
