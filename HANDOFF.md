# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival

Authority: zero-context recovery projection. Re-read live GitHub before execution; this packet self-invalidates on topology/head/event/claim drift.

## Identity
- project_id: `rot://project/agentic-os`
- objective_id: `rot://objective/agentic-os/survival-v2-cp5`
- workstream_id: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- last_reconciliation_agent_id: `rot://agent/chatgpt/graph-refactor-v2-architect`
- last_reconciliation_session_id: `rot://session/chatgpt/graph-refactor-v2/20260829T2341+0200`
- correlation_id: `graph-refactor-v2-20260829-2341`

## Authority snapshot
- repository: `rotprods/AGENTIC-OS-by-Rust`
- main observed: `4964721c48f62cefe5593837fed7dacfd1945253`
- F1 semantic/base head: `015abe49353f744269d10cec7f7d3778a46e963c`
- active branch: `feat/graph-refactor-v2-survival`
- active PR: `#4`
- observed runtime head before reconciliation commits: `856196196ce186357d9e95c37dddef74d984fc3a`
- event watermark: `0`; accepted durable Survival event authority is not qualified
- whole Survival V2 authority: `IMPLEMENTED / SHADOW_ONLY`

## Exact-head evidence for observed runtime head
- F1 Cross-Language Parity `33275978136`: PASS.
- F1 Rust Contract Kernel `33275978153`: PASS.
- Python unittest discovery in the parity workflow executes current Survival reducer/schema/store/graph/coordination/ContextPack/death-drill tests at that revision.

## What live reconciliation changed
A stale-continuity defect was found: prior `STATE.md`, `TASKS.md`, this HANDOFF and machine state still referenced PR #3 and an obsolete NOT_RUN frontier although PR #4 had advanced significantly. The reconciliation wave:

- published a non-canonical `HELLO/WORK_STARTED` coordination record for the new session;
- persisted `evidence/graph-refactor-v2/LIVE_TRUTH_RECONCILIATION_2026-08-29.md`;
- corrected `STATE.md`, `TASKS.md` and `state/project_state.json`;
- added `graph/live_truth_snapshot.v2.json` with explicit invalidation semantics;
- preserved the distinction between reference verification and production qualification.

## Current capability graph
### Verified/reference-verified
- F1 Rust kernel and F1 TS/Python parity at observed PR #4 runtime head;
- Python Survival V2 reducer/checkpoint/freshness semantics;
- Python reference append-only store and deterministic replay/idempotency tests;
- Python one-way graph projection/rebuild tests;
- Python claims/barriers/coordination tests;
- Python ContextPack invalidation tests;
- synthetic death-drill evaluator tests;
- Survival schemas/adversarial corpus.

### Still blocked
1. Survival behavioral parity across Rust + TypeScript + Python.
2. pnpm lockfile/frozen dependency resolution.
3. semantic supersession audit of PR #2's seven unique commits.
4. empirical zero-context <=5 minute death drill.
5. accepted durable event writer / non-zero authoritative event watermark.
6. local revision manifest for external governance authorities.

## PR topology warning
PR #2 and PR #4 are **git-diverged**. Comparison from PR #2 head to observed PR #4 head reports PR #4 ahead by 111 commits and behind by 7. Do **not** close or mark PR #2 superseded until those seven unique commits are semantically audited. Historical truth must be preserved.

## Next safe parallel wave
- A — Rust owner: implement Survival behavioral contract parity against frozen shared fixture.
- B — TypeScript owner: same behavioral contract parity; no independent semantics.
- C — Migration owner: inspect PR #2-only commits and map each requirement/file/decision to KEEP/REFACTOR/SUPERSEDE.
- D — DevSecOps owner: create pnpm lockfile and frozen-install CI; record dependency evidence.
- E — Security owner: expand threat model/corpus for prompt/provider poisoning, secrets/PII, path/URL/shell injection and evidence substitution.

A/B share contract/fixture semantic scope and require fencing/serialization around fixture mutation. C/D/E are intended to be file-disjoint.

## Hard prohibitions
- no production authority claim from simulator/unit-test success;
- no reverse-write from COS/ContextPack/GraphRAG/projections into canonical authority;
- no PR #2 closure without supersession evidence;
- no PostgreSQL/Redis/Kafka/Kubernetes/vector DB merely for symmetry;
- no durable/multi-host promotion before behavioral parity + recovery/security gates.

## Resume recipe
1. Read `AGENTS.md`.
2. Read `STATE.md`, `TASKS.md`, `state/project_state.json` and `graph/live_truth_snapshot.v2.json`.
3. Read `evidence/graph-refactor-v2/LIVE_TRUTH_RECONCILIATION_2026-08-29.md`.
4. Re-fetch live main, PR #1/#2/#4, PR #4 head and latest Actions runs.
5. Invalidate this handoff if head/topology/event watermark/claims changed.
6. Inspect existing scope claims before mutation.
7. Continue only from the current executable frontier.

## NEXT_ITERATION_METAPROMPT
**VERIFY LIVE TRUTH BEFORE EXECUTION.**

Reconstruct repository/main, PR #1/#2/#4 topology, current PR #4 head, exact-head CI, event watermark, active claims, current project state and latest evidence. If the live graph still matches the reconciled architecture, continue the P0 gate: freeze one Survival V2 behavioral golden corpus and implement equivalent state/checkpoint/freshness/replay semantics in Rust and TypeScript without diverging from the Python reference. Fail closed on any semantic disagreement. In parallel, audit PR #2-only semantics and lock the TypeScript dependency graph. Do not promote production authority, close historical PRs, or introduce distributed infrastructure until evidence gates permit it. Persist every material state/task/graph/evidence/handoff delta before finishing.
