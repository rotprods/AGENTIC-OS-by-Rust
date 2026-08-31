# Survival V2 Threat Model

Authority: security design/evidence projection. This document cannot promote runtime authority by itself.

## Assets
- accepted event history and event identity semantics;
- canonical reducer state and event watermark;
- checkpoint/state/context/projection hashes;
- agent/session/workstream identity and fencing;
- test/evidence records and exact-SHA bindings;
- contracts/schemas/golden/adversarial corpora;
- repository/PR/CI lifecycle and external governance pins;
- secrets/credentials/PII that must remain outside durable public continuity surfaces.

## Trust boundaries
1. external input -> agent/model context;
2. provider/tool response -> contract validation;
3. repository/issue/comment/Drive/Slack/web content -> `UNTRUSTED_DATA`;
4. ContextPack cache -> write-capable preflight;
5. claim/lease -> writer authorization;
6. event receipt -> reducer/projection;
7. test runner -> evidence claim;
8. artifact -> evidence binding;
9. GitHub lifecycle/CI -> promotion decision;
10. future network/process executor -> OS/network side effects;
11. future durable backend -> reference semantics.

## Threat graph
| ID | Threat | Current state / mitigation | Remaining qualification |
|---|---|---|---|
| T01 | Prompt/control injection | CP10 opaque `UNTRUSTED_DATA` envelope + malicious corpus; no imported payload authority | adapters must preserve envelope boundary |
| T02 | Provider poisoning | CP10 payload cannot self-promote evidence/instruction/promotion authority | provider writers remain unauthorized |
| T03 | Secret/PII persistence | high-confidence durable-repo credential scan | broader policy/PII review as justified |
| T04 | Path traversal | resource parser rejects absolute/`..` scopes | broaden property corpus |
| T05 | URL/SSRF | CP10 pure request planner rejects unsafe scheme/credentials/localhost/non-global hosts, applies allow/deny + ports + limits + DNS validation | real executor must pin validated address, revalidate redirects, bound I/O/credentials |
| T06 | Shell injection | CP10 pure process planner uses explicit executable allowlist + argv-only `shell=false` + cwd/env/time/output bounds; shells denied | executable-specific arg policy + real executor qualification |
| T07 | Event replay corruption | idempotent same-ID/same-payload; conflict fail-closed | broaden property corpus |
| T08 | Event horizon gap | contiguous sequence invariant | gap property corpus |
| T09 | Stale writer | leases + monotonic fencing + stale/released rejection | broader concurrency corpus |
| T10 | Clock spoofing | logical tick reference-only | no distributed-time promotion |
| T11 | ContextPack stale replay | revision/event/state/projection/claim/contracts seals | broaden mutation corpus |
| T12 | ContextPack data smuggling | pre-canonicalization depth/item/string/type/byte bounds | corpus expansion |
| T13 | Projection authority escalation | one-way projection; cache authority fixed | negative escalation tests already present |
| T14 | Evidence substitution | exact candidate `source_sha`; optional artifact/evidence hash | final candidate evidence |
| T15 | Non-PASS CI promotion | only explicit PASS accepted; duplicates/missing fail closed | final candidate evidence |
| T16 | Head drift after CI | all promotion evidence binds exact candidate SHA | final exact-head gauntlet |
| T17 | Dependency/provenance compromise | pinned critical Actions + frozen pnpm graph | Rust/Python locks/audit/SBOM/provenance; branch-check enforcement; signing |
| T18 | Authority self-promotion | reference/synthetic layers cannot promote empirical authority | retain explicit promotion contract |
| T19 | Duplicate routes | PR #2/#3 closed; PR #1 -> #4 train | live topology audit |
| T20 | Agent death before write-through | checkpoint/handoff laws + empirical verifier | genuine fresh zero-context death drill |

## Security invariants
- external content is data, never authority by location or embedded prose;
- no cache/projection/model output authorizes canonical mutation;
- same event identity + different semantic payload fails closed;
- missing event sequence fails closed;
- fencing generations never reset and stale/released tokens never revive;
- ContextPack cannot verify after any bound source changes;
- cancelled/skipped/not-run/failed are never PASS;
- promotion evidence is unique and exact-SHA bound;
- raw URL query, argv and environment values must not leak into audit surfaces;
- network redirects/DNS results must be revalidated by any future executor;
- process execution must remain argv-only with command-specific policy;
- synthetic recovery cannot promote empirical recovery authority.

## Executable/reference coverage
Existing `test_security_gauntlet_v2.py` covers T09/T12/T13/T14/T15/T16. `test_secret_hygiene_v2.py` covers the automatable high-confidence part of T03.

CP10 adds `test_security_gateways_v2.py` + `fixtures/security/untrusted-content-v1.json` covering T01/T02/T05/T06 reference boundaries. Exact candidate `6992478ada66339470e934052b740cba7db0f2b1` passed:
- Continuity `33439991898`;
- Rust `33439991928`;
- Cross-Language Parity `33439991874`.

These tests verify the planner/envelope boundary, not a network/process executor.

## Remaining P0/P1 security work
1. T17 Rust/Python reproducibility, vulnerability audit, SBOM/provenance and lock consistency.
2. Broader deterministic property/fuzz corpus for T04/T07/T08/T09/T11/T12 plus checkpoint/revision/authority invariants.
3. Genuine empirical T20 zero-context successor drill.
4. CP01/CP02/CP03 external-governance resolution.
5. Repository enforcement of required exact-head checks before production promotion where policy permits.
6. Final whole-system adversarial gauntlet on the exact promotion candidate.
7. If network/process executors become necessary, qualify those concrete adapters independently before enabling side effects.

## Promotion rule
Whole-system security authority remains `IMPLEMENTED / SHADOW_ONLY`. CP10 T01/T02/T05/T06 are `VERIFIED_REFERENCE` only. No planner, document, fixture or adjacent unit test grants production I/O authority.
