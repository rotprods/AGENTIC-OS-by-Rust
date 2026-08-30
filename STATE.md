# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + accepted events/contracts + revision-pinned evidence outrank this file when stale. Reconstruct live truth before mutation.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / SHADOW_ONLY`

## Current objective
Resolve the remaining external governance authorities, empirically prove fresh zero-context successor recovery, finish the continuity security gauntlet, and only then qualify durable accepted-event authority without prematurely promoting distributed infrastructure.

## Canonical topology
- `main`: bootstrap.
- PR #1: F1 contract kernel head `015abe49353f744269d10cec7f7d3778a46e963c`; base of the Survival stack.
- PR #2: CLOSED/UNMERGED `SUPERSEDED_UNMERGED_HISTORY` after seven-file semantic audit and V2 migration of the standalone survival metaprompt.
- PR #3: CLOSED/UNMERGED duplicate promotion route; superseded.
- PR #4: `feat/graph-refactor-v2-survival`; sole active Survival V2 promotion route, stacked on PR #1.

## Revision-pinned evidence chain
Behavioral parity implementation proof at `5952b4c792ef7ca6996f1ca82cd04b1b11bbb431`:
- Survival V2 Continuity Gate `33296938445`: SUCCESS.
- F1 Rust Contract Kernel `33296938432`: SUCCESS.
- F1 Cross-Language Parity `33296938433`: SUCCESS.

Security slices:
- head `7163acbdb4ec8245ca2c2f0cb9fb07153e4b8727`, Continuity run `33297181677`: SUCCESS. Covers executable adversarial T09/T12/T13/T14/T15/T16.
- head `d42bf0f78f3905b3472b7e05cf9afc5ad8781eaa`, Continuity run `33297209666`: SUCCESS. Adds high-confidence durable-repository secret hygiene gate for T03.

External governance contract:
- head `b61b6974faeb7a632917b4b2f26dc82a8fcc74fd`, Continuity run `33297367442`: SUCCESS.
- `rot.knowledge/main` observed/pinned at `621550ddf725c0c3d1e41540ee878be124dfe871`.
- `cos-graph-engine/main` / `COS2` observed/pinned at `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`.
- CP01, CP02 and CP03 remain unresolved and therefore block governance readiness by contract rather than being guessed.

Later state/documentation commits move the branch beyond these proof heads. Requalify the exact promotion candidate before any promotion.

## Implemented / verified reference capabilities
- F1 Rust/TS/Python contract kernel surfaces;
- Survival reducer/freshness behavioral parity across Rust, TypeScript and Python;
- structured cross-runtime Survival rejection codes;
- Survival checkpoint/freshness semantics;
- reference append-only event store + deterministic recovery/replay;
- one-way deterministic Survival/COS graph projection;
- claims/leases/fencing reference kernel with monotonic generations;
- ContextPack sealing/invalidation with `UNTRUSTED_DATA`, iterative pre-canonicalization depth/item/string/type bounds and total byte budget;
- promotion evidence preflight requiring unique explicit PASS evidence bound to exact candidate SHA, with optional artifact/evidence hash requirement;
- deterministic external-governance manifest validation/drift preflight;
- synthetic agent-death recovery harness;
- strict project-state/checkpoint schemas with `state_hash` binding;
- standalone Agent Survival Metaprompt V2;
- PR #2 semantic supersession evidence;
- threat/trust-boundary model T01–T20 with executable security slices;
- frozen pnpm workspace dependency graph in CI.

## Explicit remaining gaps
1. **Empirical recovery:** genuinely fresh zero-context successor drill <=5 minutes has not run; synthetic recovery is not empirical qualification.
2. **Governance:** CP01/CP02/CP03 authoritative locators remain unresolved. Manifest is implemented but promotion readiness intentionally fails closed.
3. **Security:** T01/T02 provider/prompt corpus, T05 network/URL/SSRF gateway, T06 argv-only shell gateway, T17 Rust/Python dependency/SBOM hardening, broader property corpus and final exact-candidate adversarial gauntlet remain.
4. **Durable authority:** accepted durable event writer is not qualified; authoritative event watermark remains `0`.
5. **Distributed authority:** multi-host/distributed infrastructure remains intentionally deferred until a measured contention/HA trigger exists.

## Authority
Whole Survival V2 remains `IMPLEMENTED` / `SHADOW_ONLY`. Individual reference capabilities may be `VERIFIED` only at cited exact revisions. External governance readiness is `BLOCKED_EXTERNAL` because CP01/CP02/CP03 are unresolved. `EMPIRICALLY_QUALIFIED` and production authority remain unauthorized.

## Current executable frontier
1. resolve CP01/CP02/CP03 authoritative locators without inference/guessing;
2. execute genuinely fresh zero-context successor death drill;
3. implement provider/network/shell security gateway contracts and broaden adversarial/property corpus;
4. bootstrap/operator CLI only around already-verified, non-dangerous primitives;
5. run final whole-system exact-candidate gauntlet;
6. only after these gates, qualify durable accepted-event persistence.
