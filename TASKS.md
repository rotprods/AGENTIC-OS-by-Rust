# TASKS — Agent Survival V2

Authority: planning projection. Reference verification and production qualification are distinct.

## Reconciled status — CP14
- [x] **SV2-001 — Exact-head combined runtime CI** — CP14 semantic candidate `5baf4b2c...` passed Continuity, Rust, Parity, Property Union, Operator CLI and Supply Chain. Every later SHA requires all applicable gates again.
- [x] **SV2-002 — PR topology** — canonical train remains PR #1 -> PR #4; CP14 lane #12 integrated without force; superseded lanes preserved as history.
- [x] **SV2-003 — Rust/TS/Python behavioral parity**.
- [x] **SV2-004R — Reference accepted-event store** — reference only; durable authority unqualified.
- [x] **SV2-005R — COS one-way projection adapter**.
- [x] **SV2-006R — Claims/barriers coordination reference**.
- [x] **SV2-007R — ContextPack compiler/invalidation reference**.
- [ ] **SV2-008 — Empirical death drill — HARD GATE** — verifier/schema VERIFIED; real fresh successor NOT RUN.
- [ ] **SV2-009 — Security / promotion gauntlet — HARD GATE**
  - [x] T01/T02/T03/T05/T06/T09/T12/T13/T14/T15/T16 reference/executable coverage.
  - [x] T17 exact locks, pinned runtimes/actions, audits and SBOM/evidence gate.
  - [x] deterministic property union for durable replay/atomicity/fencing.
  - [x] fail-closed promotion control-plane policy + live readiness observer.
  - [ ] T20 genuine independent empirical drill.
  - [ ] external GitHub required-check/PR/no-force-push/no-deletion/admin enforcement.
  - [ ] cryptographically verified/signed canonical head and signature enforcement.
  - [ ] final whole-system exact-candidate gauntlet after external hard gates close.
- [ ] **SV2-010 — Operator UX — PARTIAL / FAIL-CLOSED**
  - [x] `status`, `doctor`, `context` read-only.
  - [ ] `init`, `claim`, `checkpoint`, `handoff` intentionally `AUTHORITY_UNQUALIFIED`.
  - [ ] `recover` intentionally `CAPABILITY_UNQUALIFIED`.
- [x] **SV2-011 — Cross-language supply-chain reproducibility** — Cargo/pnpm/Python locks exact; runtime/tooling pins; Action SHA pins; audits and Rust/Python CycloneDX. Native pnpm CycloneDX deferred without independent justification for a major upgrade.
- [ ] **SV2-012 — External governance manifest — BLOCKED_EXTERNAL** — CP01/CP02/CP03 unresolved; never infer nominal collisions.
- [ ] **SV2-013 — Durable accepted-event authority** — watermark remains `0`; do not begin qualification until empirical + governance + GitHub promotion gates close.

## Highest-value safe frontier
1. Apply signed-head + required-check/PR/no-force-push/no-deletion/admin enforcement through an authorized GitHub write path; rerun the observer and require `READY`.
2. Resolve CP01/CP02/CP03 only from unique revision-pinned durable evidence.
3. Run empirical death drill only from a genuinely fresh independent runtime.
4. Run final exact-candidate adversarial qualification only after all three external hard-gate families close.
5. Then qualify a simple single-host durable accepted-event writer.
6. Keep network/process executors and distributed infrastructure deferred until a measured requirement exists.
