# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival

## Identity
- project_id: `rot://project/agentic-os`
- objective_id: `rot://objective/agentic-os/survival-v2-cp5`
- workstream_id: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- agent_id: `rot://agent/chatgpt/graph-refactor-v2-architect`
- session_id: `rot://session/chatgpt/graph-refactor-v2/20260829T2118+0200`
- correlation_id: `graph-refactor-v2-survival-convergence`

## Authority snapshot
- observed semantic source: F1 head `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0` — durable Survival event store is not implemented yet
- branch: `feat/graph-refactor-v2-survival`
- PR: `#3`
- CP4 evidence source head: `6f2c74a1471a6af336c1df3318cab49884291189`
- CP4 authority: `VERIFIED` for Python reference Survival layer only
- whole Survival V2 authority: `IMPLEMENTED`, not VERIFIED/PRODUCTION

## Why this branch exists
Survival V1 PR #2 was branched from bootstrap `main` while the real F1 runtime lived in PR #1. That created two parallel architectural truths. This branch begins exactly from PR #1 head and adds Survival V2, producing one combined candidate whose CI can prove integration before any prior PR is superseded.

## Completed
- reconstructed live topology and detected wrong-base Survival V1 defect;
- compiled V2 architecture, authority hierarchy, lexicon, gap matrix and 20D COS hypergraph ontology;
- persisted canonical `/GRAPH-REFACTOR-V2` execution prompt;
- created 17-checkpoint implementation program;
- added strict Survival project-state/checkpoint schemas;
- added deterministic Python reducer, freshness seal, checkpoint integrity and death-drill evaluator;
- fixed escaped failure families: duplicate semantic event identity, sequence rewind, bool watermark coercion, wrong list types, self-referential Git HEAD model and checkpoint tampering;
- pinned GitHub Actions checkout/Rust toolchain/cache refs to exact commits;
- created README/STATE/TASKS/ADR/HANDOFF recovery surfaces.

## Verification
At code head `6f2c74a1471a6af336c1df3318cab49884291189`:
- F1 Rust Contract Kernel run `33271402509`: PASS.
- F1 Cross-Language Parity run `33271402511`: PASS; its Python discovery included Survival V2 reducer/schema tests at that revision.
- Survival Rust↔TS↔Python parity: NOT_RUN / not implemented.
- COS projection rebuild parity: NOT_RUN.
- claims/concurrency: NOT_RUN.
- ContextPack invalidation: NOT_RUN.
- synthetic real zero-context <=5 minute death drill: NOT_RUN.

The commits adding this checkpoint/state/handoff moved the branch after the above PASS. Re-run clean CI on the current final head before any promotion or supersession.

## Code/security review
- Survival reference code is in-memory contract logic; no network/shell/filesystem/provider writes.
- schema surfaces are `additionalProperties:false`.
- stale source/event/projection seals fail closed.
- critical GitHub Actions are commit pinned.
- remaining supply-chain gap: TypeScript parity package has no lockfile, so pnpm transitive resolution is not fully reproducible.
- external governance refs CP01/CP02/CP03/rot.knowledge are not yet revision-pinned locally.

## Graph delta
- Session, Checkpoint, Authority, Decision, Test, Evidence, Claim and EventWatermark are first-class continuity entities.
- COS dimensions L0/L1/L2/L3/L6/L8/L9/L12/L13/L14/L15 are planned/active views; non-relevant dimensions explicitly NOT_APPLICABLE.
- projections are one-way derived state and may never reverse-write authority.

## Blockers
1. current post-handoff head must pass exact-head combined CI;
2. Rust/TS/Python Survival contract parity;
3. reference accepted-event store/replay snapshot semantics;
4. COS deterministic rebuild parity;
5. claims/barriers/concurrency semantics;
6. ContextPack freshness/invalidation;
7. synthetic zero-context death drill;
8. pnpm lockfile/reproducibility;
9. revision-pinned external governance references.

## Next safe actions
1. Reconstruct live main/PR #3 and run/inspect exact-head Rust + parity CI.
2. If green, implement `SV2-003` Survival Rust↔TS↔Python golden parity; do not supersede PR #1/#2 until final convergence evidence proves coverage preservation.
3. Implement reference append-only event store and deterministic snapshot/replay semantics.
4. Implement one-way COS adapter/rebuild parity only after event/state semantics are frozen.
5. Then claims/barriers → ContextPack invalidation → real death drill.

## Resume recipe
1. Read `AGENTS.md`.
2. Read `prompts/GRAPH_REFACTOR_V2.md`.
3. Read `state/project_state.json`, `STATE.md`, `TASKS.md`, `docs/ARCHITECTURE_V2.md`, `docs/GAP_MATRIX_V2.md` and latest checkpoint.
4. Re-read live GitHub `main`, PR #1/#2/#3 and current CI; live lifecycle outranks this handoff if changed.
5. Confirm no competing scope claims before mutation.
6. Continue CP5 only from fresh truth.

## NEXT_ITERATION_METAPROMPT
**VERIFY LIVE TRUTH BEFORE EXECUTION.**

Reconstruct `main`, PR #3 head/CI, active scopes, current state/checkpoint and applicable contract versions. If unchanged and exact-head CI is green, continue `SV2-003`: implement shared Survival V2 golden fixtures and equivalent Rust/TypeScript/Python semantics for canonical project-state/checkpoint/freshness/replay behavior. Preserve CP4 Python behavior, fail closed on semantic disagreement, and do not begin COS runtime or distributed infrastructure before parity is proven. After every material change run the adversarial gauntlet, persist evidence/state/graph/task/decision deltas, then compile the next safe wave. This packet is acceleration only; invalidate it if live truth differs.
