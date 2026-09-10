# HARDNESS V1 — Self-Hosting Assurance Protocol

Authority: DERIVED_POLICY_ONLY
Scope: CGEV2/GGEV2 execution assurance
Owner: Hardness workstream
Source revision: feat/hardness-v1-self-hosting
Supersedes: informal hardness design notes

## North Star
No material change may gain higher authority unless the rigor proportional to its risk, blast radius and historical failure profile has been executed and evidenced on the exact candidate revision.

## Operating model

Hardness surrounds the CGEV2 execution lifecycle:

BEFORE -> DURING -> AFTER -> LEARNING -> NEXT ITERATION

### BEFORE
- preflight
- live-truth freshness
- scope compilation
- authority ceiling
- risk classification
- required gate compilation

### DURING
- runtime guard
- head drift
- claim/lease/fencing checks
- unexpected mutation detection
- evidence binding

### AFTER
- unit/integration/contract tests as applicable
- regression tests
- property/fuzz/mutation/chaos according to hardness level
- recovery/death drill according to hardness level
- refactor review
- promotion decision

### LEARNING
Every escaped bug compiles into:

Bug -> RootCause -> BrokenInvariant -> RegressionTest -> FailureFamily -> ProtocolRule

The learning record is durable. A chat explanation alone is not learning.

## Profiles

- H0: docs / low-risk reversible changes
- H1: ordinary application code
- H2: critical business logic / public contracts
- H3: stateful, concurrent or distributed behavior
- H4: authority, secrets, security boundaries
- H5: production-critical, irreversible or global-control-plane changes

Profiles are monotonic: H(n+1) inherits all required skills/gates from H(n).

## Hard laws

1. Unknown risk fails closed.
2. Evidence must match repo + ref + exact full SHA.
3. A PASS from another SHA is historical evidence only.
4. Hardness cannot grant canonical project authority; it only emits GO/NO_GO recommendations constrained by evidence.
5. Production authority requires H5.
6. A missing required gate is NO_GO.
7. A failed required gate is NO_GO.
8. Projection data cannot become authority merely by being present in GGEV2.
9. Self-hosting changes to Hardness are H5 until explicitly reduced by a future verified policy revision.
10. No distributed infrastructure is introduced by Hardness itself.

## Self-hosting execution

Hardness V1 is built under H5.

### CP-H0 — Live truth + scope
Entry: current GGEV2 branch and head reconstructed.
Exit: isolated branch + issue + authority ceiling persisted.

### CP-H1 — Profile/skill ontology
Exit: H0-H5 monotonic profile compiler + deterministic plan hash.

### CP-H2 — Policy/promotion engine
Exit: stale exact-head evidence rejected; missing/failed gates rejected; bounded GO possible only with complete evidence.

### CP-H3 — Learning loop
Exit: escaped bug cannot be persisted without root cause, invariant, regression test, failure family and protocol rule.

### CP-H4 — Adversarial gauntlet
Required attacks:
- unknown risk
- malformed SHA
- stale SHA evidence substitution
- failed gate represented alongside passing unrelated evidence
- attempt to promote H0 directly to production
- authority regression through promotion API
- non-monotonic profile regression
- incomplete learning record

### CP-H5 — Exact-head qualification
All applicable tests must run against the final candidate SHA. If docs/state updates alter the SHA, rerun the gate.

### CP-H6 — Integration-ready
Hardness may be consumed by /autoprompting and GGEV2 only after CP-H5. Consumption remains projection/policy only.

## Definition of Done
V1 is not DONE unless:
- implementation exists;
- self-hosting tests execute and pass;
- H0-H5 monotonicity is tested;
- unknown risk fails closed;
- exact-head binding is tested;
- production requires H5;
- learning record completeness is tested;
- CI is exact-head green;
- evidence and handoff are durable;
- no unresolved P0/P1 discovered by the V1 gauntlet;
- another zero-context agent can identify the next safe task without this conversation.
