# TASKS — Agent Survival V2

Authority: planning projection. Completion requires implementation + executed evidence + security review + durable state/graph/handoff updates. Reference implementation and production qualification are distinct states.

## Reconciled status — CP6

- [x] **SV2-001 — Exact-head combined runtime CI**
  - Latest pre-checkpoint proof: head `2600ca4edfbe4eb05cf5d91c00027eb9fa9c0a31`.
  - Survival V2 Continuity run `33278482090`: SUCCESS.
  - F1 Rust run `33278482108`: SUCCESS (`fmt + clippy + unit tests`).
  - F1 parity run `33278482051`: SUCCESS, including TypeScript Survival behavioral verifier and Python test discovery.
  - Any later head must be requalified before promotion.

- [x] **SV2-002 — Reconcile/supersede PR topology**
  - PR #3 duplicate promotion route: CLOSED/UNMERGED SUPERSEDED.
  - PR #2 Survival V1: seven unique file surfaces audited, standalone metaprompt migrated to V2, then CLOSED/UNMERGED as `SUPERSEDED_UNMERGED_HISTORY`.
  - Evidence: `evidence/graph-refactor-v2/PR2_SEMANTIC_SUPERSESSION_AUDIT_2026-08-30.md`.
  - Canonical train: `main -> PR #1 F1 -> PR #4 Survival V2`.

- [ ] **SV2-003 — Survival Rust/TS/Python behavioral parity** — **P0/P1 boundary**
  - Rust consumes `fixtures/golden/survival-behavior-v2.json`: PASS at `2600ca4e...`.
  - TypeScript consumes the same corpus: PASS at `2600ca4e...`.
  - Python now consumes the same corpus: PASS via Continuity Gate at `2600ca4e...`.
  - Remaining gap: Python `SurvivalContractError` does not expose the structured cross-runtime `error_code`; transitional verifier maps exact messages to fixture codes.
  - DoD: make error code part of Python contract and delete message-based adapter; rerun all three exact-head.

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
  - Threat model now persisted at `docs/THREAT_MODEL_SURVIVAL_V2.md` with T01–T20 trust-boundary/failure families.
  - Existing tests cover replay, sequence gaps, stale writers, fencing, path traversal, stale/tampered ContextPacks and projection escalation.
  - Remaining: automated secret/dependency checks, property/fuzz corpus, future URL/shell/provider gateway attacks, evidence substitution, final whole-system gauntlet.

- [ ] **SV2-010 — Bootstrap/install UX**
  - Target: `agentic-os init/status/context/claim/checkpoint/handoff/recover/doctor`.
  - Depends on contract/error parity + recovery/security gates.

- [ ] **SV2-011 — Supply-chain reproducibility** — **P1 NEXT**
  - Commit pnpm lockfile and require frozen install.
  - Pin/record Python dependency set used by CI.
  - Add dependency evidence/SBOM when surface stabilizes.

- [ ] **SV2-012 — External governance revision manifest** — **P1 NEXT**
  - Revision-pin CP01/CP02/CP03/rot.knowledge authority references and detect drift.

- [ ] **SV2-013 — Durable accepted-event authority**
  - Current event watermark remains `0`; reference EventStore is not production authority.
  - Implement/qualify only after parity/recovery/security gates. Start local/durable simple; no distributed backend without measured contention trigger.

## Highest-value safe frontier
1. structured Python Survival error-code contract; remove transitional message mapper;
2. pnpm lockfile + frozen CI install;
3. empirical fresh-agent death drill;
4. external governance revision manifest;
5. threat-model automation/property/fuzz tests.

These tracks are file-disjoint except contract/error parity must coordinate with shared behavioral corpus owners.

## Deferred until measured trigger
PostgreSQL, Redis, Kafka, Kubernetes, multi-host workers, vector DB, production GraphRAG, GraphQL, MCP/A2A and Mission Control remain `DEFERRED_DECISION`.
