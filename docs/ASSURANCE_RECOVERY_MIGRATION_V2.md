# Assurance, Security, Recovery, Migration & Parallelization V2

## Test architecture
Critical categories: unit, contract, JSON Schema, property, mutation, cross-language golden parity, integration, E2E, concurrency, replay/idempotency, recovery, security, performance, empirical qualification and agent-death drill.

### Escaped-bug corpus to preserve
- mutable action refs → pin supply-chain dependencies;
- state artifact cannot self-reference its containing Git SHA → use `observed_source_sha` + external artifact revision;
- duplicate same event identity/different payload → fail closed;
- same sequence/different event → fail closed;
- stale source/event/projection → reject continuation;
- boolean masquerading as numeric sequence → reject;
- skipped/cancelled/not-run != PASS;
- command/request != outcome;
- projection/cache != authority;
- branch isolation != semantic ownership;
- correlation != causation;
- provider timeout after acceptance → reconcile before retry;
- main changes after CI → combined-head proof required;
- JSON Schema formats require real FormatChecker where formats are used.

Every escaped defect must map ROOT_CAUSE→INVARIANT→REGRESSION_TEST→ADJACENT_FAILURE_FAMILY.

## Security model
### Assets
Identity contracts, accepted events, evidence, secrets, source code, claims/authority, release state, graph/state projections.

### Trust boundaries
GitHub issues/comments/branches, external web/Drive/Slack/provider responses, imported prompts, media/archive parsers, ContextPacks, LLM/GraphRAG output, shell/filesystem/URL inputs.

### Threats
Prompt/control-plane injection; secret/PII persistence; path traversal; SSRF/file URLs; shell injection; malicious archives/media; dependency/action compromise; replay/evidence substitution; stale writer; authority self-promotion; duplicate external spend; graph/cache poisoning.

### Mitigations
Default-deny authority; strict schemas/types; canonical identities/hashes; revision-pinned evidence; immutable event semantics; one-way projections; bounded untrusted-data serialization; action pins; preflight irreversible operations; eventual leases/fencing only where runtime contention justifies them.

Residual risks are explicit nodes; no `security PASS` claim without an executed security gate.

## Recovery model
Destroyable without losing project continuity: chat history, model memory, local checkout, ContextPack, COS snapshots, indexes, dashboards and local reference DB.

Recovery sources: repository contracts/code, accepted event history, revision-pinned evidence and accepted decision history. Rebuild canonical state first, then graph, then bounded ContextPack.

### Recovery parity acceptance
- same project/objective/source revision/event horizon;
- same active workstreams/claims/barriers;
- same verified/unverified capability sets;
- same blockers and next safe action;
- same canonical graph hash within versioned projection rules.

### Agent death SLO
<=5 minutes tool/machine time and <=1 bounded ContextPack. Score against canonical state, not human impression.

## Migration plan
### M0 Current topology
`main` bootstrap; PR #1 F1 kernel; PR #2 parallel Survival V1; PR #3 combined candidate.

### M1 Convergence proof
Run exact-head PR #3 Rust/parity/Survival tests and inspect diff for lost #1/#2 semantics.

### M2 Supersession
If M1 green, mark PR #1/#2 SUPERSEDED by #3; do not delete them. If unique behavior is missing, preserve until ported.

### M3 Contract parity
Port Survival schemas/reducer/freshness semantics to Rust + TypeScript and add shared goldens.

### M4 Runtime/reference state
Add append-only reference event store/snapshots and coordination semantics.

### M5 COS projection
Implement one-way adapter against version-pinned COS semantics and graph rebuild parity.

### M6 Recovery/Context
Add ContextPack + invalidation + recovery CLI + death drill.

### M7 Production promotion
Only after assurance/security gates and explicit authority decision. Operational database/network layers require measured trigger.

## Parallelization
After Survival contract schema freeze:
- Track A: Rust/TS/Python parity (owns survival contract implementation/goldens).
- Track B: COS projection adapter (owns adapter + graph tests, not event authority).
- Track C: assurance/security (owns gauntlet/tests/threat artifacts, read-only contracts).
- Track D: recovery/DX (owns CLI/runbooks/death drill, consumes stable contracts).

Single-owner during mutation: event schema, state schema, identity semantics, accepted authority hierarchy. Two agents touching the same semantic contract coordinate even if files differ.

## CI/CD model
Local-first where execution environment exists; GitHub clean runner is merge authority. Before irreversible promotion: reread live main/event horizon/claims/barriers, run combined-head exact revision, code review, security review, then one promotion at a time and verify post-merge main.

## Definition of Done — Program
V2 is not DONE until executable continuity contracts have cross-language parity; event/state replay and graph rebuild are deterministic; zero-context death drill meets SLO; security gauntlet has no unresolved P0/P1; documentation/state/graph are consistency-checked; recovery does not require chat; residual unknowns are explicit and owned.
