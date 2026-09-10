# TASKS — Agent Survival V2

Authority: planning projection. Reference verification, exact locator resolution, GitHub lifecycle state and production qualification are distinct.

## Reconciled status — CP16
- [x] **SV2-001 — Exact-head runtime qualification infrastructure** — ancestor CI is never reused as final proof.
- [x] **SV2-002 — Canonical PR topology** — PR #1 -> PR #4 remains the promotion train; CP15 integration is consumed at `d19009055fb86e33836706fd0f09991869311431`; CP16 is isolated as PR #28 until live GitHub says otherwise.
- [x] **SV2-003 — Rust/TS/Python behavioral parity**.
- [x] **SV2-004R — Reference accepted-event store** — reference only; durable authority unqualified.
- [x] **SV2-005R — COS one-way projection adapter**.
- [x] **SV2-006R — Claims/barriers coordination reference**.
- [x] **SV2-007R — ContextPack compiler/invalidation reference**.
- [ ] **SV2-008 — Empirical death drill — HARD GATE** — verifier/schema implemented; real fresh successor remains NOT RUN in this session.
- [ ] **SV2-009 — Security / promotion gauntlet — HARD GATE**
  - [x] T01/T02/T03/T05/T06/T09/T12/T13/T14/T15/T16 reference/executable coverage.
  - [x] T17 exact locks, pinned runtimes/actions, audits and SBOM/evidence gate as last qualified before CP16; re-audit runtime deprecation findings when observed.
  - [x] deterministic property union for durable replay/atomicity/fencing.
  - [x] fail-closed promotion control-plane policy + live readiness observer.
  - [x] isolated GitHub-native merge path empirically proven capable of producing a verified PGP-signed commit.
  - [ ] T20 genuine independent empirical drill.
  - [ ] external GitHub required-check/PR/no-force-push/no-deletion/admin enforcement.
  - [ ] signed-head enforcement.
  - [ ] final whole-system exact-candidate gauntlet after external hard gates close.
- [ ] **SV2-010 — Operator UX — PARTIAL / FAIL-CLOSED**
  - [x] `status`, `doctor`, `context` read-only.
  - [ ] `init`, `claim`, `checkpoint`, `handoff` intentionally `AUTHORITY_UNQUALIFIED`.
  - [ ] `recover` intentionally `CAPABILITY_UNQUALIFIED`.
- [x] **SV2-011 — Cross-language supply-chain reproducibility** — Cargo/pnpm/Python locks exact; runtime/tooling pins; Action SHA pins; audits and Rust/Python CycloneDX. Native pnpm CycloneDX remains explicitly deferred.
- [ ] **SV2-012 — External governance manifest — LOCATORS RESOLVED / PROMOTION BLOCKED**
  - [x] CP01 exact canonical governance document candidate located.
  - [x] CP02 exact canonical governance document candidate located.
  - [x] CP03 exact canonical governance document candidate located.
  - [x] manifest v2 encodes all three as `CANDIDATE_PINNED`, never final authority.
  - [ ] CP01 explicit governance release transition.
  - [ ] CP02 parent CP-0300 compatibility + complete MID01 machine manifest + independent review/owner decision.
  - [ ] CP03 predecessor compatibility + MID02 + PostgreSQL/RLS/backend parity + independent architecture/security review/owner decision.
- [ ] **SV2-013 — Durable accepted-event authority** — watermark remains `0`; do not begin qualification until empirical + governance-promotion + GitHub promotion gates close.
- [x] **SV2-014 — CP10/CP16 checkpoint continuity authority repair**
  - [x] latest checkpoint dynamically resolved from `state.latest_checkpoint_id`; no hardcoded CP filename.
  - [x] latest checkpoint binds the pre-pointer state by rewinding only `latest_checkpoint_id` to the parent.
  - [x] drift in blockers/authority/watermark/capabilities/source/claims/workstreams/next actions invalidates the binding.
  - [x] malformed ID, traversal, missing checkpoint, ID mismatch, payload/state hash tamper fail closed.
  - [x] deterministic sequential checkpoint transitions tested.
  - [x] cycles/self-parent/orphan/fork/partial-write/rollback families covered.
  - [x] current latest path remains URI-derived; legacy ancestors may be indexed only by unique internal ID from the bounded checkpoint directory so immutable CP5 history is preserved without becoming current path authority.
  - [x] stale ContextPack checkpoint pointer explicitly tested as freshness invalidation.
- [x] **SV2-015 — Survival child-lane pre-merge core gates**
  - [x] Continuity now triggers on PRs targeting `feat/graph-refactor-v2-survival`.
  - [x] F1 Rust now triggers on PRs targeting Survival.
  - [x] F1 Parity now triggers on PRs targeting Survival.
  - [x] Supply/Property/CLI already had this behavior.
- [x] **SV2-016 — Consumed-transition continuity rule** — canonical current state/docs may not keep an unconditional instruction to perform an already-consumed checkpoint integration transition.

## Cross-lane maintenance
- [ ] **GGEV2 snapshot refresh** — PR #18 was reconstructed as based on canonical Survival `d19009055...`. If PR #28 is merged and Survival advances, refresh/rebuild its exact-source snapshot before treating it as semantically current. Do not force-rewrite compatible concurrent work.

## Highest-value safe frontier
1. Configure required exact-head checks + PR/no-force-push/no-deletion/admin + signed-head enforcement through an authorized GitHub control-plane write path and independently observe the controls active.
2. Complete CP01/CP02/CP03 promotion governance without confusing exact locator knowledge for authority.
3. Accept/verify the empirical death drill only from a genuinely fresh independent runtime.
4. Run the final whole-system exact-candidate adversarial qualification after those hard gates close.
5. Qualify a simple single-host durable accepted-event writer only after all hard gates pass; keep event watermark `0` until then.

## Lifecycle rule for CP16
PR #28 lifecycle is external live state, not a durable unconditional task. Always fetch it first. OPEN means candidate-only; MERGED means transition consumed; changed head/base means requalification is mandatory. Never replay a merge because an old handoff says to do so.
