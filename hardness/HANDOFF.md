# Hardness V1 — Zero-Context Handoff

Authority: RECOVERY_ACCELERATOR_NOT_AUTHORITY
Program: HARDNESS-V1-SELF-HOSTING
Repo: rotprods/AGENTIC-OS-by-Rust
Branch: feat/hardness-v1-self-hosting
Base branch: feat/ggev2-r3-live-swarm

## VERIFY LIVE TRUTH BEFORE EXECUTION

Do not trust the SHA in this document as current until GitHub is re-read. This handoff accelerates recovery only.

## North Star
No material change may gain higher authority unless rigor proportional to risk, blast radius and historical failure profile has been executed and evidenced on the exact candidate revision.

## Current architecture

CGEV2 execution context
  -> Hardness compile_hardness()
  -> H0-H5 profile
  -> executable SkillSpec lifecycle graph
  -> required exact-head gates
  -> /autoprompting successor packet
  -> GGEV2 DERIVED_READ_ONLY Hardness projection
  -> promotion recommendation GO/NO_GO

Hardness cannot create canonical events, merge, update refs, or self-promote.

## Verified core
Candidate db769f584a03c387256527c30c13e899463a717c passed:
- Hardness V1 Self-Hosting Gate / run 34467543000
- GGEV2 R2 Portfolio Collectors / run 34467542994
- GGEV2 R3-R4 Swarm and Incident Engine / run 34467542955

Evidence: hardness/evidence/HARDNESS_V1_CORE_QUALIFICATION_2026-09-10.json

## Implemented surfaces
- python/rot_ai/hardness.py
- python/rot_ai/autoprompting.py
- python/rot_ai/ggev2_hardness.py
- python/tests/test_hardness.py
- python/tests/test_hardness_properties.py
- python/tests/test_autoprompting.py
- python/tests/test_ggev2_hardness.py
- hardness/HARDNESS_PROTOCOL_V1.md
- hardness/self-hosting-plan.v1.json
- .github/workflows/hardness-v1-ci.yml

## Critical residual work
The H5 compiler already REQUIRES mutation, fuzz, chaos, death-drill and supply-chain gates, but not all are first-class executable Hardness adapters yet. Therefore full H5 empirical qualification is NO_GO.

### Next safe waves
H-W5: bounded mutation + deterministic fuzz executors
H-W6: chaos/recovery + fresh-agent death drill
H-W7: supply-chain + final exact-candidate evidence bundle
H-W8: integrate Hardness as default CGEV2 execution policy only after H-W7

## Mandatory invariants
- Unknown risk => BLOCKED.
- Higher risk/requested level may never reduce hardness.
- Evidence must match repo + ref + exact full SHA.
- Only literal PASS is passing evidence.
- H0/H1/H2/H3/H4 cannot recommend authority above their configured ceilings.
- Even H5 GO is recommendation only; canonical promotion remains external authority.
- GGEV2 projection cannot mutate/promote.
- Every escaped bug must create root-cause + invariant + regression + failure-family + protocol-rule record.

## Stop conditions
Stop/fail closed on live-truth drift, overlapping mutation scope, authority ambiguity, P0/P1 regression, exact-head drift, failed required gate, or missing evidence.
