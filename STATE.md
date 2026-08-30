# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + accepted events/contracts + revision-pinned evidence outrank this file when stale. Reconstruct live truth before mutation.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

## Current objective
Empirically prove fresh zero-context successor recovery, automate the continuity security gauntlet, revision-pin external governance dependencies, and only then qualify durable accepted-event authority without prematurely promoting distributed infrastructure.

## Canonical topology
- `main`: bootstrap.
- PR #1: F1 contract kernel head `015abe49353f744269d10cec7f7d3778a46e963c`; base of the Survival stack.
- PR #2: CLOSED/UNMERGED `SUPERSEDED_UNMERGED_HISTORY` after seven-file semantic audit and V2 migration of the standalone survival metaprompt.
- PR #3: CLOSED/UNMERGED duplicate promotion route; superseded.
- PR #4: `feat/graph-refactor-v2-survival`; sole active Survival V2 promotion route, stacked on PR #1.

## Latest revision-pinned implementation proof before CP8 state writes
At `5952b4c792ef7ca6996f1ca82cd04b1b11bbb431`:
- Survival V2 Continuity Gate run `33296938445`: SUCCESS.
- F1 Rust Contract Kernel run `33296938432`: SUCCESS.
- F1 Cross-Language Parity run `33296938433`: SUCCESS.
- Rust, TypeScript and Python execute the same frozen `fixtures/golden/survival-behavior-v2.json` corpus.
- Python now emits structured Survival error codes matching Rust/TypeScript and no longer relies on message-fragment adapters.
- pnpm workspace lockfile and frozen CI installation are active.

The CP8 documentation/state commits move the branch beyond `5952b4c7...`; exact-head CI must be green again before promotion.

## Implemented / verified reference capabilities
- F1 Rust/TS/Python contract kernel surfaces;
- Survival reducer/freshness behavioral parity across Rust, TypeScript and Python;
- structured cross-runtime Survival rejection codes for the shared corpus;
- Survival Python checkpoint/freshness semantics;
- reference append-only event store + deterministic recovery/replay;
- one-way deterministic Survival/COS graph projection;
- claims/leases/fencing reference kernel with monotonic generations;
- ContextPack sealing/invalidation with `UNTRUSTED_DATA` bounds;
- synthetic agent-death recovery harness;
- strict project-state/checkpoint schemas with `state_hash` binding;
- standalone Agent Survival Metaprompt V2;
- PR #2 semantic supersession evidence;
- threat/trust-boundary model T01–T20;
- frozen pnpm workspace dependency graph in CI.

## Explicit remaining gaps
1. empirical fresh zero-context successor drill <=5 minutes has not run; synthetic recovery is not empirical qualification.
2. continuity security gauntlet is not yet fully automated: secret/dependency checks, property/fuzz corpus and evidence-substitution/provider-gateway attacks remain.
3. external CP01/CP02/CP03/rot.knowledge references are not revision-pinned locally.
4. accepted durable event writer is not qualified; authoritative event watermark remains `0`.
5. Python dependency reproducibility/SBOM can be hardened beyond the now-closed pnpm reproducibility gate.
6. distributed/multi-host authority remains intentionally deferred until a measured contention/HA trigger exists.

## Authority
Whole Survival V2 remains `IMPLEMENTED` SHADOW_ONLY. Individual reference capabilities are `VERIFIED` at exact revisions. `EMPIRICALLY_QUALIFIED` and production authority are unauthorized.

## Current executable frontier
1. empirical zero-context successor death drill;
2. security/property/fuzz automation derived from `docs/THREAT_MODEL_SURVIVAL_V2.md`;
3. external governance revision manifest and drift detector;
4. bootstrap/operator CLI around verified primitives;
5. only after these gates, qualify durable accepted-event persistence.
