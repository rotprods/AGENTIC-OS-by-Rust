# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP6

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** This packet invalidates on branch/head/event/claim/contract drift.

## Identity
- project_id: `rot://project/agentic-os`
- objective_id: `rot://objective/agentic-os/survival-v2-cp6`
- workstream_id: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- agent_id: `rot://agent/chatgpt/graph-refactor-v2-architect`
- session_id: `rot://session/chatgpt/graph-refactor-v2/20260830T0011+0200`
- correlation_id: `graph-refactor-v2-survival-cp6`

## Canonical topology
- repo: `rotprods/AGENTIC-OS-by-Rust`
- F1 semantic/base head: `015abe49353f744269d10cec7f7d3778a46e963c`
- active branch: `feat/graph-refactor-v2-survival`
- active PR: `#4`, stacked on PR #1
- PR #2: CLOSED/UNMERGED `SUPERSEDED_UNMERGED_HISTORY` after seven-file semantic audit
- PR #3: CLOSED/UNMERGED duplicate route
- event watermark: `0`; durable accepted-event authority remains unqualified
- whole Survival V2 authority: `IMPLEMENTED / SHADOW_ONLY`

## Last fully qualified code/evidence head before CP6 documentation writes
`2600ca4edfbe4eb05cf5d91c00027eb9fa9c0a31`

Exact outcomes:
- Survival V2 Continuity Gate run `33278482090`: `SUCCESS`.
- F1 Rust Contract Kernel run `33278482108`: `SUCCESS` (`cargo fmt --check`, clippy, unit tests).
- F1 Cross-Language Parity run `33278482051`: `SUCCESS`.
- TypeScript Survival behavioral verifier: PASS inside parity run.
- Rust shared behavioral corpus: PASS inside Rust unit tests.
- Python shared behavioral corpus: PASS inside Continuity/Python discovery.

The later CP6 state/docs/checkpoint commits move the branch beyond this SHA. Re-run all applicable gates on the final head before promotion.

## Major work completed
- V2 Survival architecture/ontology/lexicon/gap/implementation compiler persisted;
- reference deterministic reducer, accepted-event store/recovery bundle, one-way graph projection, claims/leases/fencing, ContextPack and synthetic death drill implemented and tested;
- checkpoints require `state_hash`; event sequence gaps and conflicting replay fail closed;
- logical ticks explicitly marked reference-only, not clock authority;
- external ContextPack payload marked/bounded `UNTRUSTED_DATA`;
- dedicated Survival V2 Continuity CI gate added;
- shared Survival behavioral corpus implemented in Rust + TypeScript + Python test surfaces;
- historical Rust fmt escaped bug repaired and exact-head Rust fmt/clippy/tests verified;
- PR #2 semantic supersession audit persisted and PR #2 closed without rewriting history;
- `prompts/AGENT_SURVIVAL_METAPROMPT_V2.md` preserves the standalone operational survival interface;
- `docs/THREAT_MODEL_SURVIVAL_V2.md` models T01–T20 threats/trust boundaries.

## Important assurance boundary
Do **not** claim full structured Rust↔TypeScript↔Python error-contract parity yet. Python `SurvivalContractError` has no structured `error_code`; `test_survival_behavior_corpus_v2.py` uses an explicitly transitional exact-message→code adapter. Behavioral accept/reject/state outcomes are exercised across all three runtimes, but structured Python rejection identity remains a real gap.

## Current blockers / debt
1. Python structured Survival error-code contract.
2. pnpm lockfile + frozen TypeScript install.
3. empirical fresh zero-context successor recovery <=5 minutes.
4. durable accepted-event writer/non-zero authoritative event watermark.
5. local revision manifest for CP01/CP02/CP03/rot.knowledge.
6. automated threat-model property/fuzz/secret/dependency evidence.

## Current graph delta
- `PR2 -> PR4` semantic migration edge is complete; PR2 promotion route is SUPERSEDED.
- `BehavioralCorpus` now has TESTED_BY edges from Rust, TypeScript and Python surfaces.
- `ErrorCodeContract(Python)` remains BLOCKS fully structured parity.
- `Threat`/`TrustBoundary`/`Mitigation` nodes T01–T20 are documented.
- synthetic `DeathDrill` proves mechanics only; empirical successor evidence remains absent.

## Resume recipe
1. Read `AGENTS.md`, `prompts/AGENT_SURVIVAL_METAPROMPT_V2.md`, `prompts/GRAPH_REFACTOR_V2.md`.
2. Read `STATE.md`, `TASKS.md`, `state/project_state.json`, latest checkpoint `state/checkpoints/cp6-behavioral-reference-20260830.json` and this HANDOFF.
3. Re-fetch live branch/PR #4, base PR #1 and exact check-runs. If head differs, invalidate exact-head claims above.
4. Inspect active scopes before mutation.
5. Highest-value safe task: structured Python `SurvivalContractError.code` parity and removal of the transitional mapping, unless live state shows another P0/P1 owner/conflict.
6. After every material mutation run Continuity + Rust + parity gates on the same final SHA, then update evidence/state/checkpoint.

## NEXT_ITERATION_METAPROMPT
**VERIFY LIVE TRUTH BEFORE EXECUTION. THIS PACKET IS ACCELERATION, NOT AUTHORITY.**

Reconstruct live PR #4 head, F1 base head, check-runs, event watermark, active scopes, `state/project_state.json` and CP6. If unchanged, continue the highest-value gap: make Python Survival errors expose the same structured cross-runtime codes used by `fixtures/golden/survival-behavior-v2.json`, migrate existing Python raises without weakening current fail-closed behavior, delete the transitional message-to-code adapter, and execute the shared corpus plus full Continuity/F1 Rust/F1 parity gates on one exact head. Then attack supply-chain reproducibility, empirical zero-context death drill and governance revision pinning. Do not introduce distributed infrastructure or production authority without measured triggers and exact evidence.
