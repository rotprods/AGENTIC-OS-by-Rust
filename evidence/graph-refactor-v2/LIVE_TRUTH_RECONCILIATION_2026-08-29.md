# GRAPH-REFACTOR-V2 — Live Truth Reconciliation — 2026-08-29

Authority: evidence record derived from live GitHub lifecycle, repository tree, durable state surfaces and exact-head CI. It does not promote runtime authority.

## Session
- project_id: `rot://project/agentic-os`
- agent_id: `rot://agent/chatgpt/graph-refactor-v2-architect`
- session_id: `rot://session/chatgpt/graph-refactor-v2/20260829T2341+0200`
- workstream_id: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- objective_id: `rot://objective/agentic-os/survival-v2-cp5`
- correlation_id: `graph-refactor-v2-20260829-2341`

## Reconstructed live topology
- repository: `rotprods/AGENTIC-OS-by-Rust`
- main: `4964721c48f62cefe5593837fed7dacfd1945253`
- PR #1 / F1 contract kernel: head `015abe49353f744269d10cec7f7d3778a46e963c`, base `main`
- PR #2 / Survival V1: head `6d9c3111891b8359296f60c02294ed1d251b0889`, open draft, historical/supersession candidate
- PR #4 / Survival V2 hypergraph continuity kernel: observed head `856196196ce186357d9e95c37dddef74d984fc3a`, base PR #1 branch, open draft
- PR #4 exact-head F1 Cross-Language Parity run `33275978136`: `SUCCESS`
- PR #4 exact-head F1 Rust Contract Kernel run `33275978153`: `SUCCESS`
- event watermark: `0`; accepted durable Survival event writer remains unqualified

## Authority defect found
`STATE.md`, `TASKS.md`, `HANDOFF.md` and `state/project_state.json` lagged the runtime and still referred to PR #3 plus several components as NOT_RUN. Live PR #4 contains and tests reference implementations for:

- append-only Survival store / replay semantics;
- one-way Survival graph projection and rebuild tests;
- claims/barriers/coordination semantics;
- ContextPack freshness/invalidation;
- synthetic death-drill evaluator;
- schema/adversarial Survival tests.

This is a continuity defect because a zero-context successor following those projections would choose an obsolete frontier.

## Correct authority classification
- F1 Rust kernel on observed PR #4 head: `VERIFIED` by CI.
- F1 Python/TypeScript parity surface on observed PR #4 head: `VERIFIED` by CI.
- Survival V2 Python reference store/graph/coordination/ContextPack/death-drill test suite: `EXECUTED + VERIFIED_REFERENCE` by Python discovery inside parity CI.
- Survival Rust↔TypeScript↔Python behavioral parity: `NOT_IMPLEMENTED / NOT_VERIFIED`.
- empirical zero-context human/agent recovery <=5 minutes: `NOT_RUN`.
- durable accepted event writer / multi-host authority: `NOT_IMPLEMENTED`.
- production authority: `NOT_AUTHORIZED`.

## Historical regression
Survival V1 and the F1 kernel originated on different branch histories. Comparing PR #2 head to PR #4 observed head reports `diverged`, with PR #4 ahead by 111 commits and behind by 7 relative to PR #2. Therefore PR #2 must not be closed merely from architectural intent; its seven unique commits require semantic/file-level supersession verification first.

## V2 architecture delta
1. **Authority plane** remains append-only accepted events + contracts + evidence; projections cannot reverse-write.
2. **Reference continuity plane** is now substantially implemented in Python and exercised on exact head.
3. **Cross-language continuity kernel** is the primary missing contract boundary and remains the next hard gate.
4. **Graph runtime** remains a derived projection, not a database authority.
5. **Distributed infrastructure** remains deferred until measured single-host limits justify it.
6. **Documentation state** must be revision/freshness aware because stale continuity documentation is itself a failure mode.

## Ranked gaps
| Gap | Severity | Blast radius | Current detection | Target |
|---|---|---:|---|---|
| Survival behavioral parity absent in Rust/TS | P0 gate | contract/runtime divergence | golden/schema CI only | shared behavioral corpus + implementations |
| durable state projections stale vs live GitHub | P1 continuity | successor chooses wrong work | manual reconciliation | live topology reconciliation + freshness seal |
| PR #2 unique history not semantically reconciled | P1 migration | lost requirements/history | compare reports divergence | file/decision supersession audit |
| empirical <=5m death drill not executed | P1 recovery | recovery SLO unproven | synthetic evaluator only | real zero-context drill artifact |
| pnpm lockfile absent | P1 supply chain | non-reproducible TS resolution | CI comment only | committed lockfile + frozen install |
| accepted durable event writer unavailable | P1 authority | event watermark remains 0 | explicit authority ceiling | implement only after parity contracts freeze |
| external governance revisions not locally pinned | P1 provenance | semantic drift | handoff warning | revision manifest + validation |

## COS dimensional status
- L0 visual architecture: `IMPLEMENTED_DOCUMENTARY`, executable visualization deferred.
- L1 execution graph: `IMPLEMENTED_DOCUMENTARY`; frontier reconciled here.
- L2 state machine: `IMPLEMENTED_REFERENCE`.
- L3 dependency graph: `IMPLEMENTED_DOCUMENTARY`.
- L4 call graph: `PARTIAL`; no automated call-graph artifact yet.
- L5 control flow: `PARTIAL`; critical reference paths tested, no global CFG artifact.
- L6 dataflow: `IMPLEMENTED_REFERENCE` for continuity pipeline.
- L7 compute graph: `NOT_APPLICABLE_YET`; no measured compute bottleneck.
- L8 knowledge graph: `IMPLEMENTED_DOCUMENTARY`.
- L9 semantic graph: `IMPLEMENTED_DOCUMENTARY` through lexicon/ontology.
- L10 embedding similarity: `NOT_APPLICABLE` as authority; optional discovery only.
- L11 GraphRAG: `DEFERRED`; no production need proven.
- L12 memory graph: `IMPLEMENTED_REFERENCE` through state/checkpoint/ContextPack model.
- L13 agent graph: `IMPLEMENTED_REFERENCE` through coordination model.
- L14 tool graph: `IMPLEMENTED_DOCUMENTARY`.
- L15 workflow graph: `IMPLEMENTED_REFERENCE` for reference continuity flows.
- L16 network graph: `NOT_APPLICABLE` until multi-host trigger.
- L17-L19: `NOT_APPLICABLE` until domain-specific need is demonstrated.

## Next safe executable frontier
1. Reconcile durable state/docs to PR #4 live truth without claiming production authority.
2. Implement Survival V2 behavioral parity in Rust + TypeScript from one shared golden corpus.
3. Add a frozen pnpm lockfile and fail CI on unlocked dependency resolution.
4. Audit the seven PR #2-only commits and explicitly preserve/supersede each semantic requirement.
5. Execute a real zero-context recovery drill after parity and topology reconciliation.

## Stop condition for this reconciliation wave
`SUCCESS` means stale durable continuity surfaces are corrected and CI for the resulting documentation/state head is green. It does **not** mean Survival V2 or G1 is production-ready.
