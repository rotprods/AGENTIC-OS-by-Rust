# STATE — Agent Survival V2

Authority: human-readable projection only. `state/project_state.json` is the machine projection; live GitHub lifecycle + accepted events/evidence outrank both when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

## Current objective
Converge the verified F1 contract kernel with Agent Survival V2 and prove CP4 reference contracts without introducing a second source of truth.

## Current topology
- `main`: bootstrap only.
- PR #1: F1 Rust/TS/Python contract kernel; exact head `015abe49353f744269d10cec7f7d3778a46e963c` had Rust + parity workflows green before V2 convergence.
- PR #2: Survival V1 originally branched from empty main; historical/supersession candidate only until convergence coverage is proven.
- PR #3: canonical combined candidate based on #1 + V2 Survival architecture/tests; draft, pending current exact-head CI.

## Implemented in PR #3
- F1 contract kernel inherited intact;
- mandatory Survival V2 lifecycle in AGENTS;
- `/GRAPH-REFACTOR-V2` prompt;
- Architecture V2, Survival Protocol V2, lexicon;
- COS 20D hypergraph ontology/projection manifest;
- ranked gap matrix + implementation compiler;
- strict checkpoint/project-state schemas;
- Python deterministic survival reducer, freshness seal, checkpoint builder and death-drill evaluator;
- adversarial/schema tests;
- pinned critical GitHub Action refs;
- zero-context README/HANDOFF surfaces.

## Not yet proven
- exact-head PR #3 CI after latest changes;
- Rust/TS/Python survival contract parity;
- executable COS projection/rebuild parity;
- claims/barriers/leases runtime;
- ContextPack invalidation runtime;
- synthetic <=5 minute zero-context death drill;
- durable distributed event backend;
- multi-host authority.

## P0/P1 blockers
1. Combined PR #3 must be exact-head green before #1/#2 supersession.
2. Survival contracts need cross-language parity before promotion.
3. COS projection rebuild and death-drill evidence do not yet exist.
4. TypeScript dependency install has no lockfile; CI explicitly records this reproducibility gap.

## Authority state
`IMPLEMENTED` for Survival V2. F1 capabilities retain their revision-pinned prior verification; the combined candidate is not VERIFIED until current CI succeeds.
