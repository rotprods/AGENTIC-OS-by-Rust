# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + accepted events/contracts + revision-pinned evidence outrank this file when stale. Reconstruct live truth before mutation.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

## Current objective
Close the remaining contract/assurance gaps after shared Survival V2 behavioral execution across Rust, TypeScript and Python, then empirically prove zero-context successor recovery without prematurely promoting durable/distributed infrastructure.

## Canonical topology
- `main`: bootstrap.
- PR #1: F1 contract kernel head `015abe49353f744269d10cec7f7d3778a46e963c`; base of the Survival stack.
- PR #2: CLOSED/UNMERGED `SUPERSEDED_UNMERGED_HISTORY` after seven-file semantic audit and V2 migration of the standalone survival metaprompt.
- PR #3: CLOSED/UNMERGED duplicate promotion route; superseded.
- PR #4: `feat/graph-refactor-v2-survival`; sole active Survival V2 promotion route, stacked on PR #1.

## Latest revision-pinned proof before CP6 state/checkpoint writes
At `2600ca4edfbe4eb05cf5d91c00027eb9fa9c0a31`:
- Survival V2 Continuity Gate run `33278482090`: `SUCCESS`.
- F1 Rust Contract Kernel run `33278482108`: `SUCCESS` — formatting, clippy and unit tests all passed.
- F1 Cross-Language Parity run `33278482051`: `SUCCESS` — Python golden/schema/test discovery, TypeScript golden/schema and TypeScript Survival behavioral verifier passed.
- Python executes the same frozen `fixtures/golden/survival-behavior-v2.json` corpus via `test_survival_behavior_corpus_v2.py`.
- Rust executes that corpus via `crates/rot-survival/tests/behavioral.rs`.
- TypeScript executes that corpus in the parity workflow.

The CP6 documentation/state commits move the branch beyond `2600ca4e...`; exact-head CI must be green again before promotion.

## Implemented / verified reference capabilities
- F1 Rust/TS/Python contract kernel surfaces;
- Survival Python reducer/checkpoint/freshness semantics;
- reference append-only event store + deterministic recovery/replay;
- one-way deterministic Survival/COS graph projection;
- claims/leases/fencing reference kernel with monotonic generations;
- ContextPack sealing/invalidation with `UNTRUSTED_DATA` bounds;
- synthetic agent-death recovery harness;
- shared Rust/TypeScript/Python behavioral corpus execution;
- strict project-state/checkpoint schemas with `state_hash` binding;
- standalone Agent Survival Metaprompt V2;
- PR #2 semantic supersession evidence;
- threat/trust-boundary model T01–T20.

## Explicit remaining gaps
1. Python `SurvivalContractError` still lacks a structured cross-runtime `error_code`; the corpus verifier currently uses a transitional exact-message→code adapter. This prevents claiming fully structured error-contract parity.
2. pnpm lockfile/frozen install is missing.
3. empirical fresh zero-context successor drill <=5 minutes has not run; synthetic recovery is not empirical qualification.
4. accepted durable event writer is not qualified; authoritative event watermark remains `0`.
5. external CP01/CP02/CP03/rot.knowledge references are not revision-pinned locally.
6. distributed/multi-host authority remains intentionally deferred until a measured contention/HA trigger exists.

## Authority
Whole Survival V2 remains `IMPLEMENTED` SHADOW_ONLY. Individual reference capabilities are `VERIFIED` at exact revisions. `EMPIRICALLY_QUALIFIED` and production authority are unauthorized.

## Current executable frontier
1. structured Python Survival error-code contract, then remove transitional mapping and rerun all three runtimes;
2. pnpm lockfile + frozen dependency install;
3. empirical zero-context successor death drill;
4. external governance revision manifest;
5. automate security/property/fuzz checks from `docs/THREAT_MODEL_SURVIVAL_V2.md`;
6. only after these gates, qualify durable accepted-event persistence.
