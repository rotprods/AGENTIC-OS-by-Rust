# Agent Survival Protocol v1

## Purpose
Make agent death, chat truncation, model replacement and cross-session handoff ordinary recoverable events rather than project failures.

## Architectural principle
Authority is event-sourced. Graphs, ContextPacks, summaries and dashboards are deterministic projections/caches. The system is designed so a zero-context agent can reconstruct the actionable project state from durable artifacts without reading historical chats.

## Control planes
1. **Identity plane** — stable project/workstream/objective/agent/session/claim IDs.
2. **Event plane** — immutable causal ledger of accepted state transitions.
3. **Canonical state plane** — compact machine-readable current state derived from accepted events + repository truth.
4. **Graph projection plane** — COS multidimensional views over the same durable truth.
5. **Decision plane** — append-only ADR/decision history with supersession.
6. **Task plane** — executable DAG, blockers, ownership, value/effort and status.
7. **Evidence plane** — tests, runs, artifacts, hashes, source commits and authority scopes.
8. **Memory/knowledge plane** — facts, semantic terms, memories, TTL and provenance.
9. **Coordination plane** — claims, leases, heartbeats, barriers and handoffs.
10. **Recovery plane** — checkpoints, ContextPacks, resume recipes and disaster-reconstruction tests.

## Source-of-truth boundaries
- Git commits/contracts/schemas + accepted event ledger are durable authority.
- Database/event-store becomes operational authority only after its promotion gate is verified.
- COS graphs are rebuildable projections.
- Vector indexes/GraphRAG are retrieval accelerators.
- LLM memory/chat is advisory only.

## Required repository surface
```text
AGENTS.md
GOAL.md
TASKS.md
state/
  project_state.json
  events/YYYY-MM-DD/*.json
  checkpoints/<checkpoint_id>.json
  handoffs/<handoff_id>.md
  claims/<claim_id>.json
  evidence/index.jsonl
decisions/<decision_id>.md
graph/
  ONTOLOGY.md
  projection_manifest.json
  snapshots/
context/
  CURRENT_CONTEXT_PACK.json
  README_FIRST.md
prompts/
  AGENT_SURVIVAL_METAPROMPT.md
schemas/
  checkpoint.schema.json
  project_state.schema.json
```

## Genetic project protocol
Every project embedding this framework inherits the same identifiers, event semantics, graph ontology and recovery contract. Project-specific node/edge classes extend the core ontology; they never replace it.

### Canonical identity
Use URI-like IDs where feasible:
`rot://project/<slug>`
`rot://workstream/<project>/<slug>`
`rot://objective/<project>/<slug>`
`rot://agent/<provider>/<agent>`
`rot://session/<provider>/<uuid>`
`rot://task/<project>/<id>`
`rot://decision/<project>/<id>`
`rot://checkpoint/<project>/<uuid>`

Names are labels, never identities.

## Checkpoint strategy
Checkpoints are incremental state transitions, not transcript dumps. Every checkpoint references its parent checkpoint and event watermark. The recovery system should support binary questions: `what changed since checkpoint X?`, `what blocks objective Y?`, `what is the exact test evidence for claim Z?`, `which agent owns semantic scope S?`.

## Graph projections
COS dimensions are activated as orthogonal projections over one canonical event/state model. Minimum recommended project profile:
- L0: visualization
- L1: execution DAG
- L2: state machines
- L3: dependency/blocker graph
- L6: data/evidence lineage
- L8: knowledge/ontology
- L9: semantic vocabulary and supersession
- L11: GraphRAG retrieval
- L12: memory
- L13: agent/session/delegation
- L14: tools/providers/fallbacks
- L15: workflows/gates/retries
- L16: infrastructure/network when needed

## Recovery SLO
A zero-context capable agent should reconstruct safe next action in <=5 minutes of machine/tool time and <=1 ContextPack, without historical chat access. A mature implementation should test this with synthetic `agent death` drills.

## Death drill
At milestones, launch a fresh agent with only repository access and ask it to report:
1. north star;
2. current objective;
3. latest verified head/event watermark;
4. active owners/claims;
5. completed work;
6. current blockers;
7. exact test status;
8. unresolved decisions/debt;
9. next three executable actions;
10. unsafe ambiguities.
Score against the canonical state. Any miss is a continuity defect.

## Promotion gates
- G0 Schema validity
- G1 Event determinism/idempotency
- G2 Cross-language golden parity
- G3 Graph rebuild parity
- G4 Checkpoint recovery parity
- G5 Concurrent claim/barrier correctness
- G6 ContextPack invalidation correctness
- G7 Agent-death drill SLO
- G8 Durable event backend qualification
- G9 Multi-host contention/recovery
- G10 Production authority

## Anti-patterns
Forbidden: giant mutable `memory.md`; chat summaries as canonical truth; graph nodes mutated without events; current-state files with no event watermark; silent decision overwrite; tasks without dependencies; `tests passed` without exact evidence; branch isolation treated as ownership; generated ContextPack with no invalidation identity; deleting rejected ideas instead of superseding them.
