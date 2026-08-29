# TASKS — Agent Survival V2

Authority: planning projection. Completion requires implementation + executed evidence + security review + durable state/graph/handoff updates. Reference implementation and production qualification are distinct states.

## Reconciled status

- [x] **SV2-001 — Exact-head combined runtime CI**
  - Evidence: PR #4 observed runtime head `856196196ce186357d9e95c37dddef74d984fc3a`.
  - Rust run `33275978153`: SUCCESS.
  - parity run `33275978136`: SUCCESS.
  - Scope: F1 + discovered Python Survival suites at that revision.

- [ ] **SV2-002 — Reconcile/supersede PR topology**
  - Status: `IN_PROGRESS`.
  - Evidence: PR #2 vs PR #4 comparison is `diverged`; PR #4 is ahead by 111 commits and behind by 7 relative to PR #2.
  - DoD: audit every PR #2-only semantic/file delta; preserve or explicitly supersede it; then close historical PR only if coverage is proven.

- [ ] **SV2-003 — Survival Rust/TS/Python behavioral parity** — **P0 NEXT**
  - Existing: shared Survival golden/schema fixtures; Python reference semantics; TypeScript Survival schema verification.
  - Missing: equivalent Rust + TypeScript behavioral state/checkpoint/freshness/replay implementation and shared exact-byte/hash corpus.
  - DoD: canonical bytes/hash/state transition/schema accept-reject parity 100%; conflicting semantics fail closed.

- [x] **SV2-004R — Reference accepted-event store**
  - Scope: Python reference only, not durable authority.
  - Existing: expected revision, idempotency/conflict and deterministic replay/snapshot tests in `test_survival_store_v2.py`.
  - Promotion remains blocked by SV2-003 and durable-authority qualification.

- [x] **SV2-005R — COS one-way projection adapter reference**
  - Scope: Python reference only.
  - Existing: event/state → typed graph and deterministic rebuild tests in `test_survival_graph_v2.py`.
  - No reverse-write authority is authorized.

- [x] **SV2-006R — Claims/barriers coordination reference**
  - Scope: Python reference only.
  - Existing: conflict/lease/fencing/clock-authority adversarial tests in `test_coordination_v2.py`.
  - Distributed coordination remains deferred.

- [x] **SV2-007R — ContextPack compiler/invalidation reference**
  - Scope: Python reference only.
  - Existing: source/event/projection freshness and invalidation tests in `test_context_pack_v2.py`.
  - Write-capable production ContextPack remains unauthorized.

- [ ] **SV2-008 — Empirical agent death drill**
  - Reference simulator/evaluator: IMPLEMENTED + TESTED.
  - Missing: a genuinely fresh zero-context successor reconstructing bounded state/ownership/evidence/blockers/next actions in <=5 minutes from durable authority.
  - Simulator PASS must never self-promote this task.

- [ ] **SV2-009 — Continuity security gauntlet**
  - Existing reference tests cover multiple stale writer/replay/tamper/coordination cases.
  - Remaining: prompt/provider poisoning, secrets/PII, path/URL/shell injection, evidence substitution across artifacts, dependency compromise and explicit threat-model evidence.
  - DoD: P0/P1=0 or explicit BLOCKED with owner/mitigation.

- [ ] **SV2-010 — Bootstrap/install UX**
  - Depends on: behavioral parity and authority boundaries frozen.
  - Target surface: `agentic-os init/status/context/claim/checkpoint/handoff/recover/doctor`.
  - DoD: non-destructive adoption; no competing authority; death-drill verified.

- [ ] **SV2-011 — Supply-chain reproducibility** — **P1 NEXT**
  - Commit pnpm lockfile.
  - Change CI to frozen install.
  - Pin/record Python dependency set used for schema verification.
  - Generate dependency evidence/SBOM when implementation surface stabilizes.

- [ ] **SV2-012 — External governance revision manifest** — **P1 NEXT**
  - Pin local provenance for CP01/CP02/CP03/rot.knowledge authorities.
  - Detect semantic revision drift before write-capable execution.

## Next safe parallel wave
- Agent A: `SV2-003` Rust behavioral parity.
- Agent B: `SV2-003` TypeScript behavioral parity.
- Agent C: `SV2-002` PR #2 unique-commit supersession audit.
- Agent D: `SV2-011` dependency reproducibility.
- Agent E: `SV2-009` threat-model + adversarial corpus.

Agents A/B share contract semantics and must use a frozen fixture owner/fencing claim. C/D/E are file-disjoint and may proceed concurrently.

## Deferred until measured trigger
PostgreSQL, Redis, Kafka, Kubernetes, multi-host workers, vector DB, production GraphRAG, GraphQL, MCP/A2A and Mission Control remain `DEFERRED_DECISION`. No implementation merely for architectural symmetry.
