# Agent Survival Core Ontology v1

## Core node types
`PROJECT`, `OBJECTIVE`, `WORKSTREAM`, `MILESTONE`, `TASK`, `AGENT`, `SESSION`, `CLAIM`, `LEASE`, `FILE`, `MODULE`, `CONTRACT`, `SCHEMA`, `DECISION`, `ASSUMPTION`, `REQUIREMENT`, `RISK`, `BLOCKER`, `BUG`, `TEST`, `TEST_RUN`, `EVIDENCE`, `ARTIFACT`, `DATASET`, `PROVIDER`, `TOOL`, `ENVIRONMENT`, `BRANCH`, `COMMIT`, `PR`, `RELEASE`, `CHECKPOINT`, `HANDOFF`, `MEMORY`, `KNOWLEDGE`, `TERM`, `METRIC`, `IDEA`, `REFACTOR`, `INCIDENT`, `CONTEXT_PACK`, `EVENT`.

## Core edge types
`PARENT_OF`, `DEPENDS_ON`, `BLOCKS`, `UNBLOCKS`, `IMPLEMENTS`, `MODIFIES`, `DEFINES`, `CONSTRAINS`, `VALIDATES`, `FAILS`, `PASSES`, `PRODUCES`, `DERIVED_FROM`, `PROVES`, `CONTRADICTS`, `SUPERSEDES`, `CAUSED_BY`, `ASSIGNED_TO`, `CLAIMED_BY`, `OWNED_BY`, `EXECUTED_BY`, `RESUMES_FROM`, `HANDS_OFF_TO`, `REFERENCES`, `AFFECTS`, `RISKS`, `MITIGATES`, `TESTS`, `OBSERVED_IN`, `PROMOTES_TO`, `REJECTED_BECAUSE`, `NEXT_AFTER`, `CACHED_FROM`, `INVALIDATED_BY`.

## Temporal/provenance attributes
Every authoritative or potentially stale relation should support: `event_id`, `source_commit`, `valid_from`, `valid_to`, `authority`, `confidence`, `provenance`, `supersedes_edge_id`.

## COS projection mapping
- L0 Visual: all human-facing topology
- L1 Execution: TASK/OBJECTIVE/MILESTONE + DEPENDS_ON/NEXT_AFTER/BLOCKS
- L2 State: lifecycle state of TASK/SESSION/CLAIM/PR/RELEASE
- L3 Dependency: dependency and blocker subgraph
- L4 Call: runtime/code invocation
- L5 CFG: control-flow internals
- L6 DataFlow: DATASET/EVIDENCE/ARTIFACT + PRODUCES/DERIVED_FROM
- L8 Knowledge: KNOWLEDGE/TERM/DECISION/REQUIREMENT
- L9 Semantic: TERM, alias/equivalence/supersession relations
- L10 Embedding: non-authoritative similarity index references only
- L11 GraphRAG: ContextPack retrieval paths
- L12 Memory: MEMORY + TTL/decay/provenance
- L13 Agent: AGENT/SESSION/CLAIM/LEASE/delegation
- L14 Tool: TOOL/PROVIDER/capability/fallback
- L15 Workflow: TASK/gates/retries/automation
- L16 Network: ENVIRONMENT/services/infrastructure

## Invariants
1. Graph state is reconstructible from accepted events plus immutable repository facts.
2. No fuzzy identity creates canonical nodes.
3. `SUPERSEDES` preserves history; destructive replacement is forbidden for decisions/assumptions/evidence.
4. `PROVES` requires evidence identity and source revision.
5. ContextPack nodes are caches and must carry `CACHED_FROM` watermark plus invalidation edges.
6. A CLAIM over semantic scope can conflict even when file paths do not overlap.
