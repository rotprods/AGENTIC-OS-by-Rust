# V2 Gap / Risk Matrix

Priority is impact × probability × blast radius × strategic importance ÷ cost, with hard P0/P1 overrides.

| ID | Gap | Sev | Detection today | V2 fix | Evidence required | Phase |
|---|---|---:|---|---|---|---|
| G001 | Survival V1 branched from empty `main` instead of F1 kernel | P0 | live PR topology | converge/supersede onto exact F1 head | stacked diff + clean CI | P0 |
| G002 | Chat/context can still contain facts not durably persisted | P0 | manual | mandatory write-through/checkpoint law + death drill | synthetic zero-context recovery | P6/P11 |
| G003 | Survival contracts only prose/schemas; no deterministic reducer | P0 | architecture audit | executable reference reducer + replay tests | same input events → same state hash | P5/P6 |
| G004 | Graph ontology not executable/rebuild-proven | P1 | manual | event/state→COS adapter + projection manifest/hash | delete/rebuild→same hash | P8 |
| G005 | No current durable event backend in this runtime | P1 deferred | explicit phase boundary | reference append-only store first; network backend only on trigger | crash/replay tests | P6/P14 |
| G006 | Cross-language survival contract parity absent | P0 before promotion | CI | Rust/TS/Python golden fixtures | 100% bytes/hash/schema parity | P5/P10 |
| G007 | Claims/leases/barriers not executable in this repo | P1 | manual | reference coordination kernel after event/reducer gate | contention/takeover tests | P7 |
| G008 | ContextPack freshness/invalidation not executable | P1 | manual | source head + event horizon + projection seal | stale pack rejection tests | P9 |
| G009 | No automated agent-death drill | P0 continuity | none | deterministic recovery evaluator/harness | <=5 min/one pack success | P11 |
| G010 | README on main is effectively empty; project discoverability poor | P1 DX | inspection | V2 README after convergence | zero-context usability test | P4/P13 |
| G011 | `rot.knowledge` / CP01-03 references are external and not revision pinned in this repo | P1 governance | manual | authority manifest with exact refs/hashes where available | ref resolution test | P4 |
| G012 | Decision history only registry placeholder | P1 | inspection | ADR schema/index + supersession semantics | query/recovery test | P4/P5 |
| G013 | Test names may overstate proof scope | P1 assurance | review | evidence scope metadata + exact claims | adversarial review | P10 |
| G014 | No explicit threat model artifacts for continuity plane | P1 security | review | trust-boundary/threat graph | security gauntlet | P12 |
| G015 | No canonical current state/checkpoint/handoff instances | P0 recovery | inspection | seed machine-readable V2 state + session event/checkpoint | schema validation + successor drill | P0/P1 |
| G016 | Potential docs/state drift as surfaces grow | P1 | none | canonical state reducer + consistency gate | deliberate drift test must fail | P10 |
| G017 | Overengineering risk: premature DB/GraphRAG/network layers | P1 strategic | governance | measured-trigger policy + NOT_APPLICABLE dimensions | architecture review | all |
| G018 | Historical escaped bugs from other repos are not yet imported into reusable assurance corpus | P2/P1 depending invariant | manual | cross-project escaped-bug catalog | regression mapping | P2/P10 |

## Current critical path
`G001 → G003/G006 → G004/G007/G008 → G009 → security/recovery gauntlets → production authority`.

## Explicitly deferred
PostgreSQL, Redis, Kafka, Kubernetes, distributed workers, vector DB, GraphRAG runtime, GraphQL/MCP/A2A and Mission Control are not current blockers. Their interfaces may be designed, but operational deployment requires a measured trigger and its own ADR.
