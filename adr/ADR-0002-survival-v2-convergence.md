# ADR-0002 — Agent Survival V2 convergence and authority model

Status: ACCEPTED for SHADOW V2 candidate.

## Decision A — Survival V2 is a superset layer on the F1 kernel
Problem: Survival V1 (PR #2) was branched directly from bootstrap `main`, parallel to F1 runtime PR #1.
Alternatives: keep parallel PRs; merge #2 first then #1; retarget #2 and resolve conflicts; build a clean convergence branch from exact #1 head.
Decision: build convergence branch from exact F1 head and prove it as a combined PR to main. Only after clean evidence may #1/#2 become SUPERSEDED.
Why: preserves verified F1 implementation, prevents competing architecture/control planes, produces combined-head CI.
Risk: larger convergence diff. Mitigation: exact-head CI and coverage-preservation review.
Reconsideration trigger: unique #1/#2 functionality is shown missing from convergence.
Confidence: HIGH.

## Decision B — `observed_source_sha` instead of self-referential current HEAD
Problem: a Git-tracked state/checkpoint cannot safely contain the SHA of the commit that contains itself; changing the file changes the commit SHA.
Alternatives: write stale `head_sha`; calculate impossible self-reference; omit revision binding; distinguish upstream observed semantic source from projection artifact revision.
Decision: state/checkpoints store `observed_source_sha` + event watermark/projection seal. The commit containing the projection artifact is external provenance, not a self-field.
Why: deterministic, implementable and explicit about projection freshness.
Risk: consumers may confuse observed source with artifact revision. Mitigation: schema descriptions, lexicon and tests.
Reconsideration trigger: move state to a transactional store where row revision and source revision can be represented separately.
Confidence: HIGH.

## Decision C — Projections/cache never gain write authority
Decision: COS graph, ContextPacks, GraphRAG, dashboards and LLM summaries are rebuildable views. All write authority originates from accepted event/contract/evidence semantics.
Reason: prevents hidden second sources of truth and makes graph/cache deletion recoverable.
Confidence: HIGH.

## Decision D — Infrastructure requires measured trigger
Decision: do not introduce Postgres/Redis/Kafka/Kubernetes/vector DB/distributed workers merely to complete architecture diagrams. Specify interfaces now; deploy when concurrent multi-process authority, HA, distributed jobs, asset scale or measured performance requires them.
Tradeoff: local/reference phases have lower availability/scale. Benefit: lower cognitive/operational risk and faster assurance.
Confidence: HIGH.
