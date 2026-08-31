# TASKS — Agent Survival V2

Authority: planning projection. Completion requires implementation + executed evidence + security review + durable state/graph/handoff updates. Reference verification and production qualification are distinct states.

## Reconciled status — CP10

- [x] **SV2-001 — Exact-head combined runtime CI**
  - Latest CP10 implementation candidate: `6992478ada66339470e934052b740cba7db0f2b1`.
  - Continuity `33439991898`: PASS.
  - Rust `33439991928`: PASS.
  - Cross-Language Parity `33439991874`: PASS.
  - Any later branch head must be requalified; ancestor green is not current proof.

- [x] **SV2-002 — Reconcile/supersede PR topology**
  - PR #2 and PR #3 are CLOSED/UNMERGED historical/superseded routes.
  - Canonical train: `main -> PR #1 F1 -> PR #4 Survival V2`.

- [x] **SV2-003 — Survival Rust/TS/Python behavioral parity**
  - Shared frozen behavioral corpus; structured rejection-code parity; no message-fragment interpretation.

- [x] **SV2-004R — Reference accepted-event store**
  - Reference replay/idempotency/conflict semantics only. Durable writer authority remains unqualified.

- [x] **SV2-005R — COS one-way projection adapter**
  - Derived/non-authoritative; no reverse write.

- [x] **SV2-006R — Claims/barriers coordination reference**
  - Leases, semantic conflicts and monotonic fencing reference tested.

- [x] **SV2-007R — ContextPack compiler/invalidation reference**
  - Revision seals + `UNTRUSTED_DATA` + structural bounds. Remains `CACHE_ONLY`.

- [ ] **SV2-008 — Empirical agent death drill — P1 HARD GATE**
  - Verifier/schema/protocol: VERIFIED.
  - Real fresh zero-context successor <=300s: NOT RUN.
  - Current CP10 runtime is not independent; no synthetic submission was produced.

- [ ] **SV2-009 — Continuity security gauntlet — P1 PARTIALLY EXECUTED**
  - Existing: T03 and T09/T12/T13/T14/T15/T16 executable coverage.
  - CP10 VERIFIED_REFERENCE at `6992478...`: T01/T02 malicious external-content envelope/corpus; T05 URL/SSRF planning boundary; T06 argv-only process planning boundary.
  - The CP10 planners perform no network/process I/O and do not qualify an executor.
  - Remaining: T17 Rust/Python reproducibility/audit/SBOM/provenance; broader deterministic property/fuzz corpus; T20 empirical drill; actual executor-specific gates if those capabilities are introduced; final exact-candidate gauntlet.

- [ ] **SV2-010 — Bootstrap/operator UX**
  - Target commands remain `init/status/context/claim/checkpoint/handoff/recover/doctor`.
  - Safe non-dangerous primitives may be wrapped next; network/process execution remains unauthorized.

- [x] **SV2-011 — TypeScript supply-chain reproducibility**
  - Frozen pnpm lock/install exists.
  - Rust/Python/T17 assurance remains open under SV2-009.

- [ ] **SV2-012 — External governance manifest — IMPLEMENTED / BLOCKED_EXTERNAL**
  - `rot.knowledge` and `COS2` revision pins remain valid from the durable manifest.
  - CP01/CP02/CP03 remain `UNRESOLVED`.
  - CP10 repeated authoritative search and found no unique locator; an unrelated `Clever-Agent` CP01 was rejected as a name collision.
  - Never infer missing locators.

- [ ] **SV2-013 — Durable accepted-event authority**
  - Event watermark stays `0`.
  - Start only after empirical, governance, security and exact-candidate gates.

## Highest-value safe frontier
1. T17 Rust/Python reproducibility + vulnerability/SBOM/provenance hardening.
2. Deterministic property/fuzz corpus for event/replay/fencing/checkpoint/authority invariants.
3. Resolve CP01/CP02/CP03 only if unique authoritative evidence appears.
4. Run empirical death drill only from a genuinely fresh independent runtime.
5. Final exact-candidate whole-system gauntlet.
6. Then qualify a simple single-host durable event writer; distributed complexity remains deferred without a measured trigger.

## Promotion-assurance risk
The active branch currently has branch protection/status-check enforcement disabled, so exact-head qualification is procedural rather than repository-enforced. Add enforcement before production promotion if repository policy/permissions permit.
