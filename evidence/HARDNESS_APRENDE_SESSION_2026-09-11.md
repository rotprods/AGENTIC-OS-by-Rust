# /APRENDE — Hardness V1 self-hosting — 2026-09-11

Authority: durable learning/evidence projection. VERIFY LIVE TRUTH BEFORE EXECUTION. This file does not grant promotion authority.

## Scope
This learning cycle covers the construction of Hardness around CGEV2/GGEV2 and the failures discovered while Hardness was applied to itself.

## North Star
No material change may gain higher authority unless rigor proportional to risk, blast radius and history is executed and evidenced on the exact candidate revision.

## Learning chain

### L-001 — exact identity is necessary but insufficient
Observation: an `EvidenceRecord` could carry the correct repo/ref/SHA and literal PASS while still being caller-authored.
Root cause: structural validity was confused with provenance trust.
Broken invariant: H4/H5 promotion evidence must be independently provenance-qualified.
Generalized failure family: `EVIDENCE_OBJECT_FORGERY`.
Repair: introduce provider observations and `QualifiedEvidence`; H4/H5 reject plain evidence as `UNVERIFIED_EVIDENCE_PROVENANCE`.
Regression: forged plain evidence cannot promote H4/H5.
Protocol rule: exact-head binding is mandatory but never sufficient for trusted evidence.

### L-002 — a trusted-looking wrapper must not be caller-mintable
Observation: after introducing `QualifiedEvidence`, a caller could theoretically instantiate the wrapper directly.
Root cause: trust marker was represented by a public data type rather than a verifier-controlled minting path.
Broken invariant: qualification must be produced by verification, not asserted by construction.
Generalized failure family: `QUALIFIED_EVIDENCE_FORGERY`.
Repair: `QualifiedEvidence` uses verifier-only construction guarded by a module-private seal; direct construction fails with `QUALIFIED_EVIDENCE_CONSTRUCTION_FORBIDDEN`.
Regression: direct wrapper construction is rejected.
Protocol rule: authority-bearing capability objects require unforgeable construction paths, not merely strong field validation.

### L-003 — provider payloads are still untrusted input
Observation: verifier-minted evidence can still be wrong if the provider observation itself is ambiguous, stale, substituted or replayed.
Root cause: provider payload identity has not yet been fully bound to workflow/check-suite/artifact provenance.
Broken invariant: trusted evidence must be traceable to a live provider observation whose repository, ref, SHA, workflow/run identity and semantic conclusion all bind to the candidate.
Generalized failure family: `PROVIDER_OBSERVATION_SUBSTITUTION`.
Status: OPEN; this is H-W8.
Required regressions: stale run, wrong repo, wrong ref, wrong SHA, non-success, missing run ID, workflow substitution, duplicate/replay and artifact substitution.

### L-004 — 100% line coverage is not the assurance target
Observation: passing ordinary tests can coexist with authority bypasses.
Rule: critical invariants, changed branches, historical regressions and critical mutants are the meaningful coverage surface. Any critical surviving mutant is FAIL even if aggregate mutation score is high.
Implemented: deterministic fuzz + bounded semantic mutation campaigns.
Open: source-level mutation campaign and explicit survivor report/tool identity.

### L-005 — self-hosting evidence becomes historical whenever the head changes
Observation: persisting documentation/evidence changes the candidate SHA.
Rule: every exact-head qualification is historical immediately after a new commit. Final candidate must be frozen and all required gates rerun on that exact SHA, or a strictly documented non-executable descendant proof must exist. Prefer rerun.

### L-006 — simulated death drills cannot self-certify independence
Observation: the builder can execute recovery logic but cannot truthfully be a zero-context independent successor.
Rule: death-drill evaluator and chaos/recovery harness may be built here, but empirical PASS requires a genuinely fresh successor with no predecessor chat and only durable entrypoints.
Status: BLOCKED_EXTERNAL until independent successor executes issue #26.

### L-007 — Hardness is policy/evidence, not canonical authority
Rule: Hardness may compile required rigor and emit GO/NO_GO recommendations. GGEV2 may project Hardness state. Neither may create accepted events, merge, acquire canonical ownership or promote itself.
Current intended mode: SHADOW until final H5 qualification and explicit promotion authority.

### L-008 — reuse stronger existing gates instead of duplicating them
Observation: AGENTIC-OS already contains a deeper CP13 supply-chain gate with pinned runtimes, lock hashes, frozen installs, audits and SBOMs.
Rule: Hardness consumes and requires stronger existing evidence rather than creating weaker parallel truth.

### L-009 — mutable-provider metadata itself can drift or be stale
Observation: during this session, branch/PR metadata continued to report head `9daf88a7...` while file reads reflected later provenance hardening content. This may be connector/cache behavior or concurrent mutation and is not resolved authority.
Rule: successor MUST re-fetch branch, PR, commit history, target file blobs and CI before trusting any head stated here. Treat disagreement as `LIVE_TRUTH_INCONSISTENT` and fail closed until reconciled.

## Protocol internalization
A lesson is not considered learned because it appears in chat. It becomes operational only when promoted through:

Observation -> Root Cause -> Broken Invariant -> Failure Family -> Regression Test -> Executable Gate -> Protocol Rule -> Autoprompt -> Durable Handoff.

## Current assurance status
Implemented/verified in prior exact-head runs: H0-H5 profile compiler, monotonic risk, skill contracts, lifecycle compiler, exact-head evidence binding, authority ceilings, CGEV2 shadow adapter, GGEV2 projection, deterministic fuzz, bounded semantic mutation, chaos/recovery contract, death-drill evaluator, supply-chain preflight, caller-authored evidence rejection and verifier-minted `QualifiedEvidence`.

Still NOT sufficient for H5 empirical qualification: provider-bound provenance saturation, source-level mutation, final candidate freeze with all exact-head gates, independent death drill, external GitHub promotion enforcement where required, and explicit promotion authority.

## Stop law
Do not declare H5 `EMPIRICALLY_QUALIFIED`, global `ENFORCE`, or `PRODUCTION_AUTHORITY` from this document or predecessor chat.