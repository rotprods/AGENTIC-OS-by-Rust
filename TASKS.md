# TASKS — Agent Survival V2

Authority: planning projection. Reference verification, exact locator resolution and production qualification are distinct.

## Reconciled status — CP15
- [x] **SV2-001 — Exact-head runtime qualification infrastructure** — CP15 semantic and persistence candidates are continuously requalified after every material change; ancestor CI is never reused as final proof.
- [x] **SV2-002 — PR topology** — canonical train remains PR #1 -> PR #4; CP15 lane is PR #13. PR #14 is isolated signing evidence only.
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
  - [x] isolated GitHub-native merge path empirically proven to produce a verified PGP-signed commit.
  - [ ] T20 genuine independent empirical drill.
  - [ ] external GitHub required-check/PR/no-force-push/no-deletion/admin enforcement.
  - [ ] signed-head enforcement and final canonical signature re-observation after CP15 integration.
  - [ ] final whole-system exact-candidate gauntlet after external hard gates close.
- [ ] **SV2-010 — Operator UX — PARTIAL / FAIL-CLOSED**
  - [x] `status`, `doctor`, `context` read-only.
  - [ ] `init`, `claim`, `checkpoint`, `handoff` intentionally `AUTHORITY_UNQUALIFIED`.
  - [ ] `recover` intentionally `CAPABILITY_UNQUALIFIED`.
- [x] **SV2-011 — Cross-language supply-chain reproducibility** — Cargo/pnpm/Python locks exact; runtime/tooling pins; Action SHA pins; audits and Rust/Python CycloneDX. Native pnpm CycloneDX remains explicitly deferred.
- [ ] **SV2-012 — External governance manifest — LOCATORS RESOLVED / PROMOTION BLOCKED**
  - [x] `rot.knowledge/main` current signed pin audited through `afe43178ae492980ad0dead1b727b3092cfc5a13`.
  - [x] CP01 exact canonical governance document pinned at `48b0d1ed...`.
  - [x] CP02 exact canonical governance document pinned at `48b0d1ed...`.
  - [x] CP03 exact canonical governance document pinned at `48b0d1ed...`.
  - [x] manifest v2 encodes all three as `CANDIDATE_PINNED`, never as final authority.
  - [ ] CP01 explicit governance release transition.
  - [ ] CP02 parent CP-0300 compatibility + complete MID01 machine manifest + independent review/owner decision.
  - [ ] CP03 predecessor compatibility + MID02 + PostgreSQL/RLS/backend parity + independent architecture/security review/owner decision.
- [ ] **SV2-013 — Durable accepted-event authority** — watermark remains `0`; do not begin qualification until empirical + governance-promotion + GitHub promotion gates close.

## Highest-value safe frontier
1. Exact-head qualify CP15 after the latest benign `rot.knowledge/main` repin, then integrate through GitHub-native PR merge with `expected_head_sha`.
2. Verify the resulting canonical commit is cryptographically signed and rerun Continuity + Rust + Parity + Supply + Property + CLI plus Promotion Control Plane Readiness on that exact SHA.
3. Configure required checks + PR/no-force-push/no-deletion/admin + signed-head enforcement through an authorized GitHub control-plane write path; this connector currently exposes those controls read-only only.
4. Complete CP01/CP02/CP03 promotion governance without confusing exact locator knowledge for authority.
5. Run the empirical death drill only from a genuinely fresh independent runtime.
6. Run the final whole-system adversarial qualification, then qualify a simple single-host durable accepted-event writer.
