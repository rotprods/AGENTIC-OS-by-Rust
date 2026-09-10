# COS 20D Agent Survival Hypergraph Ontology V2

## Identity rule
Names are labels; URI/typed IDs are identity. Historical nodes/edges are never deleted to make current state look cleaner; use `SUPERSEDES`, validity windows and authority attributes.

## Core node families
Project/Program/NorthStar/Goal/Objective/Milestone/Phase/Wave/Workstream/Task/Subtask/Checkpoint/DefinitionOfDone/AcceptanceCriterion/Metric/KPI/SLO/SLA.

Repository/Branch/Commit/PullRequest/Release/File/Directory/Module/Package/Service/Function/Class/Interface/API/CLI/Workflow/Pipeline/Runtime/Environment/Provider/Tool/Dependency/InfrastructureComponent.

Architecture/Subsystem/Component/Boundary/Contract/Schema/Protocol/Event/Command/Outcome/State/Projection/Reducer/Adapter/Gateway/Store/Cache/Index/Graph/GraphProjection/ContextPack.

Fact/Claim/Assumption/Hypothesis/Insight/Idea/Concept/Term/Definition/Rule/Heuristic/Pattern/AntiPattern/Decision/Alternative/RejectedAlternative/Tradeoff/Constraint/Requirement.

Bug/Regression/Failure/FailureMode/Incident/Risk/Threat/AttackSurface/Bottleneck/SinglePointOfFailure/TechnicalDebt/RefactorOpportunity/RecoveryProcedure/Rollback/Invariant.

Test/TestSuite/TestRun/Fixture/Benchmark/Experiment/Simulation/Gauntlet/FuzzCampaign/PropertyTest/MutationTest/Evidence/Artifact/Measurement/Observation/Qualification.

Agent/Session/Role/Capability/Claim/Lease/FencingToken/Handoff/Memory/Knowledge/ToolInvocation/ContextWindow/EventWatermark/Authority.

## Edge families
Causality: CAUSES, CAUSED_BY, CONTRIBUTES_TO, TRIGGERS, PREVENTS, ENABLES, DISABLES, AMPLIFIES, REDUCES.
Dependency: DEPENDS_ON, REQUIRED_BY, BLOCKS, BLOCKED_BY, UNBLOCKS, PRECEDES, FOLLOWS, REQUIRES, OPTIONALLY_REQUIRES.
Implementation: IMPLEMENTS, IMPLEMENTED_BY, CALLS, CALLED_BY, READS, WRITES, MODIFIES, GENERATES, CONSUMES, PRODUCES, TRANSFORMS, ROUTES_TO.
Contracts: DEFINES, CONSTRAINS, VALIDATES, CONFORMS_TO, BREAKS, EXTENDS, VERSION_OF, SUPERSEDES, DEPRECATED_BY.
Evidence: PROVES, SUPPORTED_BY, MEASURED_BY, OBSERVED_BY, TESTED_BY, FAILED_BY, VERIFIED_BY, QUALIFIED_BY, CONTRADICTED_BY.
Coordination: OWNED_BY, CLAIMED_BY, EXECUTED_BY, DELEGATED_TO, HANDOFF_TO, RESUMES_FROM, COLLIDES_WITH, SHARES_SCOPE_WITH, WAITS_FOR.
Architecture: CONTAINS, PART_OF, CONNECTED_TO, EXPOSES, ISOLATES, BRIDGES, PROJECTS_TO, DERIVED_FROM, SOURCE_OF_TRUTH_FOR, CACHE_OF.
Decision: CHOSEN_OVER, REJECTED_BECAUSE, JUSTIFIED_BY, ASSUMES, RISKS, MITIGATES, CONFLICTS_WITH, ALTERNATIVE_TO.
Improvement: REFACTOR_OF, OPTIMIZES, SIMPLIFIES, GENERALIZES, SPECIALIZES, REMOVES_DUPLICATION_OF, REDUCES_RISK_OF, IMPROVES.

## Edge attributes
`type`, `authority`, `confidence`, `valid_from`, `valid_to`, `source_event`, `source_commit`, `criticality`, `strength`, `cost`, `risk`, `version`, `superseded_by`.

## Hyperedge pattern
A Decision is modeled as a relation bundle: it can simultaneously MODIFY contracts/modules, INVALIDATE tests, REQUIRE migration, INCREASE risk, SUPERSEDE an alternative and UNBLOCK a goal. Implementations may materialize this as a Decision node plus typed edges while preserving one causal/correlation identity.

## COS projections
L0 Visual: topology/orphans/hubs.
L1 Execution: objective→task→test→evidence DAG and executable frontier.
L2 State: Project/Feature/PR/Task/Artifact/Release/Agent/Session/Claim/Evidence lifecycle.
L3 Dependency: blockers, blast radius, articulation points, cycles.
L4 Call: executable call ownership/fan-in/fan-out.
L5 Control Flow: unsafe fallbacks/missing failure paths.
L6 DataFlow: source→validation→state→artifact→consumer/provenance.
L7 Compute: NOT_APPLICABLE until measured computational workloads justify it.
L8 Knowledge: facts/decisions/rules/evidence/domain knowledge.
L9 Semantic: lexicon, aliases, deprecated semantics, supersession.
L10 Similarity: NOT_APPLICABLE as authority; optional advisory dedup only.
L11 GraphRAG: bounded multi-hop retrieval; advisory cache.
L12 Memory: ephemeral/working/project/decision/procedural/historical/deprecated with TTL/invalidation.
L13 Agent: agents/sessions/capabilities/ownership/handoffs/collisions.
L14 Tool: connectors/providers/fallbacks/permissions/trust/cost.
L15 Workflow: gates/retries/compensation/irreversible actions.
L16 Network: NOT_APPLICABLE until real networked deployment exists.
L17-L19: NOT_APPLICABLE for the survival kernel.

## Mandatory traversals for every change
UPSTREAM, DOWNSTREAM, LATERAL, TEMPORAL, SECURITY, TEST, RECOVERY, AGENT, DOCUMENTATION, GRAPH, COST, COMPLEXITY and PRODUCT impact.

## Query acceptance set
A compliant projection must answer: why does a decision exist; what depends on a module; what blocks an objective; what evidence supports a claim; who owns a scope; which session caused a mutation; how to resume a workstream; what becomes stale if a contract changes; and what next action is safe.
