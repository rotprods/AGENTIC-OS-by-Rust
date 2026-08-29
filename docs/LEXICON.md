# Canonical Lexicon — ROT Agentic OS V2

Every term below is normative for agent/runtime communication.

| Term | Definition | Anti-example |
|---|---|---|
| PROPOSED | Designed but not materialized. | "Implemented" because a plan exists. |
| IMPLEMENTED | Code/config/artifact exists at an exact revision. | Code exists only in chat. |
| EXECUTED | Implementation was actually run. | Workflow created but never invoked. |
| VERIFIED | Exact revision/run has passed tests proving the stated scope. | Another SHA was green. |
| EMPIRICALLY_QUALIFIED | Real-world/physical workload evidence satisfies declared acceptance thresholds. | Unit tests only. |
| BLOCKED | Progress cannot safely continue because a required dependency/authority is unavailable. | Work is merely inconvenient. |
| DEGRADED_EXTERNAL | Local system is healthy but an external dependency is unavailable/degraded. | Treating provider outage as internal PASS. |
| SUPERSEDED | Historical object remains valid history but a newer object governs current use. | Deleting old decisions. |
| AUTHORITY | Source allowed to determine a state/claim for a defined scope. | A dashboard or chat summary. |
| EVIDENCE | Revision-pinned observation/test/artifact supporting a bounded claim. | "I checked it". |
| EVENT | Immutable accepted transition/fact with identity, causality, provenance and semantic payload. | Mutable status row. |
| COMMAND | Requested action; not proof it occurred. | Treating `deploy.requested` as deployed. |
| OUTCOME | Accepted result of an operation. | Intent/request. |
| PROJECTION | Rebuildable derived representation of authority. | Hidden mutable source of truth. |
| CONTEXTPACK | Bounded cache of relevant state/graph neighborhood with freshness seal. | Persistent project memory. |
| CHECKPOINT | Incremental durable recovery boundary tied to source head/event horizon. | Transcript dump. |
| HANDOFF | Zero-context continuation package and ownership transfer/release. | "Continue from our chat". |
| CLAIM | Declared ownership/intention over semantic/file scopes. | Merely using a branch. |
| LEASE | Time-bounded runtime ownership grant. | Permanent ownership by stale agent. |
| FENCING TOKEN | Monotonic generation proving current writer authority. | Resetting generation after release. |
| LIVE TRUTH | Current repository lifecycle + accepted event horizon + valid authority/evidence. | Old README/PR text alone. |
| HISTORICAL CLAIM | Preserved statement whose authority may have expired/superseded. | Treating an old metric as current. |
| CORRELATION | Observed relationship without causal authority. | Automatically promoted optimization rule. |
| CAUSATION | Relationship supported by an accepted causal design/evidence. | Performance coincidence. |
| P0 | Safety/correctness/authority defect requiring stop-the-line. | Cosmetic docs issue. |
| P1 | High-risk correctness/reliability/product blocker. | Optional polish. |
| CONTINUITY_DEFECT | A zero-context successor cannot safely reconstruct/resume from durable authority. | Expected onboarding effort. |

## Identity convention
Prefer canonical URI-like IDs: `rot://project/...`, `rot://objective/...`, `rot://workstream/...`, `rot://agent/...`, `rot://session/...`, `rot://task/...`, `rot://decision/...`, `rot://checkpoint/...`. Human names are labels only.
