# TASKS — Agent Survival V2

Authority: planning projection. Completion requires implementation + executed evidence + security review + durable state/graph/handoff updates. Reference implementation and production qualification are distinct states.

## Reconciled status — CP9

- [x] **SV2-001 — Exact-head combined runtime CI**
  - Exact behavioral-parity proof head: `5952b4c792ef7ca6996f1ca82cd04b1b11bbb431`.
  - Survival V2 Continuity run `33296938445`: SUCCESS.
  - F1 Rust run `33296938432`: SUCCESS.
  - F1 Cross-Language Parity run `33296938433`: SUCCESS.
  - Any later implementation head must be requalified before promotion.

- [x] **SV2-002 — Reconcile/supersede PR topology**
  - PR #3 duplicate promotion route: CLOSED/UNMERGED SUPERSEDED.
  - PR #2 Survival V1: seven unique file surfaces audited, standalone metaprompt migrated to V2, then CLOSED/UNMERGED as `SUPERSEDED_UNMERGED_HISTORY`.
  - Evidence: `evidence/graph-refactor-v2/PR2_SEMANTIC_SUPERSESSION_AUDIT_2026-08-30.md`.
  - Canonical train: `main -> PR #1 F1 -> PR #4 Survival V2`.

- [x] **SV2-003 — Survival Rust/TS/Python behavioral parity**
  - Rust, TypeScript and Python consume the same frozen `fixtures/golden/survival-behavior-v2.json` corpus.
  - Python `SurvivalContractError` exposes structured `code` while preserving existing exception messages/callers.
  - Message-fragment parity adapters were removed from Python corpus verifiers.
  - Exact-head proof at `5952b4c792ef7ca6996f1ca82cd04b1b11bbb431`: all three runtime/continuity workflows SUCCESS.

- [x] **SV2-004R — Reference accepted-event store**
  - Python reference only; deterministic expected revision, idempotency/conflict, recovery bundle and replay tests.
  - Durable writer authority remains separate and unqualified.

- [x] **SV2-005R — COS one-way projection adapter reference**
  - Deterministic event/state -> typed graph projection and rebuild parity tests.
  - No reverse-write API/authority.

- [x] **SV2-006R — Claims/barriers coordination reference**
  - File/tree/semantic conflicts, leases and monotonic fencing tested.
  - `logical_tick` explicitly reference-only; no distributed clock authority.

- [x] **SV2-007R — ContextPack compiler/invalidation reference**
  - Sealed to source/event/state/projection/claim/contracts revisions.
  - External content is `UNTRUSTED_DATA` with pre-canonicalization depth/item/string/type bounds plus total canonical byte budget.
  - ContextPack remains `CACHE_ONLY`.
  - Security structural-bomb corpus passed at head `7163acbdb4ec8245ca2c2f0cb9fb07153e4b8727`, Continuity run `33297181677` SUCCESS.

- [ ] **SV2-008 — Empirical agent death drill** — **P1 HARD GATE**
  - Synthetic simulator/recovery mechanics: IMPLEMENTED + TESTED.
  - Missing: genuinely fresh zero-context successor reconstructing truth/ownership/evidence/blockers/next actions in <=5 minutes.
  - Simulator PASS cannot self-promote empirical authority.

- [ ] **SV2-009 — Continuity security gauntlet** — **P1 PARTIALLY EXECUTED**
  - Threat model persisted at `docs/THREAT_MODEL_SURVIVAL_V2.md` with T01–T20.
  - Executable gauntlet now covers T09/T12/T13/T14/T15/T16: stale/released fencing, ContextPack structural bombs, authority escalation, evidence substitution, non-PASS CI, exact-head evidence binding.
  - Exact security-gauntlet evidence: head `7163acbdb4ec8245ca2c2f0cb9fb07153e4b8727`, run `33297181677` SUCCESS.
  - High-confidence durable-repository credential scan covers automatable T03; head `d42bf0f78f3905b3472b7e05cf9afc5ad8781eaa`, run `33297209666` SUCCESS.
  - Remaining: T01/T02 provider/prompt corpus; T05 URL/SSRF gateway; T06 argv-only shell gateway before CLI; T17 Rust/Python dependency/SBOM hardening; broader deterministic property corpus; T20 empirical death drill; final exact-candidate whole-system gauntlet.

- [ ] **SV2-010 — Bootstrap/install UX**
  - Target: `agentic-os init/status/context/claim/checkpoint/handoff/recover/doctor`.
  - No shell/network-capable gateway may be promoted before T05/T06 security contracts exist.

- [x] **SV2-011 — Supply-chain reproducibility**
  - Workspace `pnpm-lock.yaml` committed.
  - CI requires frozen pnpm workspace installation.
  - Exact-head runtime gates passed after lockfile/frozen-install change.
  - Rust/Python SBOM/dependency locking remains SV2-009/T17 assurance work.

- [ ] **SV2-012 — External governance revision manifest** — **IMPLEMENTED / BLOCKED_EXTERNAL**
  - `governance/external-authorities.v1.json` now fail-closes required authority resolution/drift.
  - `rot.knowledge/main` pinned to `621550ddf725c0c3d1e41540ee878be124dfe871`.
  - `cos-graph-engine/main` (`COS2`) pinned to `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`.
  - CP01/CP02/CP03 remain `UNRESOLVED`; no repository/path locator was uniquely verified, so no guess was persisted.
  - Deterministic preflight rejects unresolved required authority, missing observation, malformed observation or SHA drift.
  - Manifest contract evidence head `b61b6974faeb7a632917b4b2f26dc82a8fcc74fd`, Continuity run `33297367442` SUCCESS.
  - Completion requires authoritative locators + exact pins for CP01/CP02/CP03.

- [ ] **SV2-013 — Durable accepted-event authority**
  - Current event watermark remains `0`; reference EventStore is not production authority.
  - Implement/qualify only after empirical recovery, security and governance readiness. Start local/durable simple; no distributed backend without measured contention trigger.

## Highest-value safe frontier
1. resolve CP01/CP02/CP03 authoritative locators without guessing;
2. execute a genuinely fresh-agent zero-context death drill <=5 minutes;
3. extend security into provider/network/shell gateway contracts and property corpus;
4. build bootstrap/operator CLI only around non-dangerous verified primitives;
5. execute final exact-candidate whole-system gauntlet;
6. only then qualify durable accepted-event persistence.

These tracks remain authority-separated. Recovery evidence cannot self-certify empirical qualification; projections/caches cannot promote themselves; unresolved governance blocks promotion even when local CI is green.

## Deferred until measured trigger
PostgreSQL, Redis, Kafka, Kubernetes, multi-host workers, vector DB, production GraphRAG, GraphQL, MCP/A2A and Mission Control remain `DEFERRED_DECISION`.
