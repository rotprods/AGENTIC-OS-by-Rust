# TASKS — Agent Survival V2

Authority: planning projection. Completion requires implementation + executed evidence + security review + durable state/graph/handoff updates. Reference implementation and production qualification are distinct states.

## Reconciled status — CP8

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
  - Python `SurvivalContractError` now exposes structured `code` while preserving existing exception messages/callers.
  - Message-fragment parity adapters were removed from both Python corpus verifiers.
  - Exact-head proof at `5952b4c792ef7ca6996f1ca82cd04b1b11bbb431`: all three runtime/continuity workflows SUCCESS.

- [x] **SV2-004R — Reference accepted-event store**
  - Python reference only; deterministic expected revision, idempotency/conflict, recovery bundle and replay tests.
  - Durable writer authority remains separate and unqualified.

- [x] **SV2-005R — COS one-way projection adapter reference**
  - Deterministic event/state -> typed graph projection and rebuild parity tests.
  - No reverse-write API/authority.

- [x] **SV2-006R — Claims/barriers coordination reference**
  - File/tree/semantic conflicts, leases and monotonic fencing tested.
  - `logical_tick` explicitly `REFERENCE_LOGICAL_TICK_ONLY`; no distributed clock authority.

- [x] **SV2-007R — ContextPack compiler/invalidation reference**
  - Sealed to source/event/state/projection/claim/contracts revisions.
  - External content is `UNTRUSTED_DATA` with depth/item/string/serialized-size limits.
  - ContextPack remains `CACHE_ONLY`.

- [ ] **SV2-008 — Empirical agent death drill** — **P1**
  - Synthetic simulator/recovery mechanics: IMPLEMENTED + TESTED.
  - Missing: genuinely fresh zero-context successor reconstructing truth/ownership/evidence/blockers/next actions in <=5 minutes.
  - Simulator PASS cannot self-promote empirical authority.

- [ ] **SV2-009 — Continuity security gauntlet** — **P1**
  - Threat model persisted at `docs/THREAT_MODEL_SURVIVAL_V2.md` with T01–T20 trust-boundary/failure families.
  - Existing tests cover replay, sequence gaps, stale writers, fencing, path traversal, stale/tampered ContextPacks and projection escalation.
  - Remaining: automated secret/dependency checks, property/fuzz corpus, future URL/shell/provider gateway attacks, evidence substitution, final whole-system gauntlet.

- [ ] **SV2-010 — Bootstrap/install UX**
  - Target: `agentic-os init/status/context/claim/checkpoint/handoff/recover/doctor`.
  - Depends on recovery/security gates and accepted authority decisions.

- [x] **SV2-011 — Supply-chain reproducibility**
  - Workspace `pnpm-lock.yaml` committed.
  - CI requires frozen pnpm workspace installation.
  - Exact-head runtime gates passed after the lockfile/frozen-install change.
  - Future hardening: Python dependency lock/evidence and SBOM remain assurance improvements, not blockers for this closed pnpm gate.

- [ ] **SV2-012 — External governance revision manifest** — **P1 NEXT**
  - Revision-pin CP01/CP02/CP03/rot.knowledge authority references and detect drift.

- [ ] **SV2-013 — Durable accepted-event authority**
  - Current event watermark remains `0`; reference EventStore is not production authority.
  - Implement/qualify only after recovery/security/governance gates. Start local/durable simple; no distributed backend without measured contention trigger.

## Highest-value safe frontier
1. empirical fresh-agent death drill;
2. automate threat-model/property/fuzz/security checks;
3. external governance revision manifest;
4. bootstrap/operator CLI around already-verified contracts;
5. only then qualify durable accepted-event persistence.

These tracks should remain authority-separated. Recovery evidence cannot self-certify empirical qualification, and projections/caches cannot promote themselves into authority.

## Deferred until measured trigger
PostgreSQL, Redis, Kafka, Kubernetes, multi-host workers, vector DB, production GraphRAG, GraphQL, MCP/A2A and Mission Control remain `DEFERRED_DECISION`.
