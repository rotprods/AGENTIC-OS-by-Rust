# Agent Survival Protocol V2

## North Star
Agent death, context truncation and model replacement must be ordinary worker replacement events, not project-memory failures.

A zero-context authorized successor must reconstruct the bounded current truth and next safe action from durable authority in <=5 minutes without historical chat access.

## Authority hierarchy
1. accepted immutable events + revision-pinned evidence;
2. executable contracts/schemas + repository truth;
3. accepted ADR/decision history;
4. canonical state produced by deterministic reducers;
5. COS graph projections;
6. checkpoints/handoffs;
7. ContextPacks;
8. LLM summaries/chat.

Lower layers never silently override higher layers.

## One truth, many projections
The runtime MUST NOT maintain independent event buses or hidden state stores. GitHub/bootstrap events, future durable Runtime EventStore and imported evidence are surfaces of one canonical event semantics. Deduplicate logical events by canonical identity/hash. Same identity with different semantic payload = fail closed.

Canonical state is a reducer output. COS, GraphRAG, dashboards and ContextPacks are rebuildable views. No projection may reverse-write authority.

## Durable planes
- Identity: Project/Objective/Workstream/Agent/Session/Task/Decision/Event/Evidence IDs.
- Event: immutable causal transitions.
- State: bounded current reducer output.
- Decision: append-only ADR + supersession.
- Task: dependency-aware executable DAG.
- Evidence: tests, physical artifacts, hashes, run IDs, authority scope.
- Coordination: claims, leases, barriers, handoffs.
- Graph: COS multidimensional projections.
- Knowledge/Memory: facts, definitions, procedural memory, TTL/invalidation.
- Recovery: checkpoints, resume recipes, ContextPacks and death drills.

## Session lifecycle
`BOOT → RECONCILE → CLAIM → HEARTBEAT → IMPLEMENT → EVIDENCE → CHECKPOINT → PREFLIGHT → HANDOFF → RELEASE`

A session is first-class and globally unique. Branch isolation is not semantic ownership isolation.

## Write-through law
Any meaningful mutation must persist the applicable deltas before recovery cost becomes material: event, canonical state input, task state, decision trace, evidence, graph input, checkpoint and ownership state.

## Checkpoint trigger
Checkpoint when a milestone completes, >=3 meaningful mutations accumulate, architecture/contract changes, blockers/risks or test authority change, an external write occurs, ownership changes, before irreversible action, expected compaction, handoff or session end, or whenever reconstruction would exceed ~10 minutes.

## Continuity invariants
- exact source SHA and event horizon on every checkpoint/handoff;
- stale ContextPack cannot authorize writes;
- no `VERIFIED` without exact evidence;
- skipped/cancelled/not-run are distinct from PASS;
- accepted history is superseded, never rewritten;
- every active task has dependency and ownership semantics;
- every material decision records alternatives/rationale/reconsideration trigger;
- every escaped bug becomes root-cause + invariant + regression test + adjacent failure family;
- graph rebuild from canonical authority must be deterministic;
- deleting chat, local checkout, ContextPack and graph cache must not destroy project continuity.

## COS profile
Activate only dimensions that solve a real problem:
L0 visual topology; L1 execution; L2 state; L3 dependencies; L4 calls; L5 control flow; L6 evidence/data flow; L8 knowledge; L9 semantic lexicon; L11 GraphRAG retrieval; L12 memory; L13 agents/sessions; L14 tools/providers; L15 workflow/gates; L16 network only when infrastructure exists. L7/L10/L17-L19 are NOT_APPLICABLE unless a measured domain need appears.

## Recovery test
A synthetic successor receives repository access, no chat history and a bounded ContextPack. It must identify North Star, objective, exact head/event horizon, active claims, blockers, completed/verified/unverified work, tests/evidence, unresolved decisions/debt and next 3 safe actions. Misses are CONTINUITY_DEFECTs.

## Overengineering rule
Postgres, Redis, Kafka, Kubernetes, queues, vector DBs, multi-host workers or additional services require explicit measured triggers. Design interfaces early; defer operational infrastructure until needed.

## Promotion gates
G0 live topology reconciled; G1 schemas valid; G2 reducer/replay/idempotency deterministic; G3 Rust/TS/Python parity; G4 COS rebuild parity; G5 checkpoint/handoff parity; G6 claims/concurrency; G7 ContextPack invalidation; G8 death-drill SLO; G9 durable backend only on trigger; G10 multi-host only on trigger; G11 production authority.
