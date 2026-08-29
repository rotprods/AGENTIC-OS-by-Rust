# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + accepted events/contracts + verified evidence outrank this file when stale. Reconstruct live truth before mutation.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

## Current objective
Freeze and prove the Survival V2 behavioral contract across Rust, TypeScript and Python while preserving F1 semantics, one-way graph authority and zero-context recoverability.

## Live topology reconciled 2026-08-29
- `main`: bootstrap head `4964721c48f62cefe5593837fed7dacfd1945253`.
- PR #1: F1 contract kernel head `015abe49353f744269d10cec7f7d3778a46e963c`; base of the Survival V2 stack.
- PR #2: Survival V1 head `6d9c3111891b8359296f60c02294ed1d251b0889`; open draft; historical/supersession candidate only. Git history is diverged from PR #4, so its seven unique commits still require semantic supersession audit.
- PR #4: `feat/graph-refactor-v2-survival`; observed runtime head `856196196ce186357d9e95c37dddef74d984fc3a` before this reconciliation wave; canonical active Survival V2 candidate.

## Exact-head evidence at observed PR #4 runtime head
- F1 Cross-Language Parity run `33275978136`: `SUCCESS`.
- F1 Rust Contract Kernel run `33275978153`: `SUCCESS`.
- Python discovery in parity CI executes the Survival V2 reducer/schema/store/graph/coordination/ContextPack/death-drill suites present at that revision.

## Implemented and reference-verified
- F1 Rust/TS/Python contract kernel and schema/golden parity surfaces;
- deterministic Python Survival reducer/checkpoint/freshness semantics;
- reference append-only Survival store with replay/idempotency tests;
- one-way Survival graph projection/rebuild tests;
- claims/barriers/coordination reference semantics;
- ContextPack freshness/invalidation reference semantics;
- synthetic death-drill evaluator and adversarial tests;
- strict Survival project-state/checkpoint schemas;
- COS ontology/projection manifest;
- pinned critical GitHub Action refs.

## Not yet promoted / not yet proven
- Survival behavioral parity across Rust + TypeScript + Python;
- empirical fresh zero-context recovery <=5 minutes;
- frozen pnpm dependency graph / lockfile;
- semantic supersession of PR #2 unique commits;
- accepted durable event writer and non-zero authoritative event watermark;
- distributed/multi-host authority;
- production COS/GraphRAG/MCP/A2A/Mission Control runtime.

## Active P0/P1 blockers
1. `survival-cross-language-parity`: reference behavior exists primarily in Python; Rust/TS behavioral equivalence is not frozen.
2. `typescript-lockfile-missing`: TS dependency resolution remains reproducibility-sensitive.
3. `pr2-semantic-supersession-unproven`: git comparison is diverged; no safe closure until unique semantics are audited.
4. `death-drill-not-empirically-executed`: simulator tests are not an empirical zero-context drill.
5. `durable-event-authority-not-qualified`: event watermark remains `0`; provisional session records are non-canonical.
6. `external-governance-revisions-unpinned`: CP01/CP02/CP03/rot.knowledge provenance needs local revision manifest.

## Authority state
`IMPLEMENTED` for Survival V2 as a shadow/reference system. Specific capabilities above are VERIFIED at revision-pinned evidence; whole-system `VERIFIED`, `EMPIRICALLY_QUALIFIED` and `PRODUCTION` claims remain unauthorized.

## Current executable frontier
1. Survival Rust/TS/Python behavioral parity from one shared corpus.
2. pnpm lockfile + frozen-install CI.
3. PR #2 seven-commit semantic supersession audit.
4. real zero-context death drill after parity is green.
5. only then qualify accepted-event persistence and broader runtime promotion.
