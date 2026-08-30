# Survival V2 Threat Model

Authority: security design/evidence projection. This document cannot promote runtime authority by itself.

## Assets
- accepted event history and event identity semantics;
- canonical reducer state and event watermark;
- checkpoint/state/context/projection hashes;
- agent/session/workstream identity;
- claims, leases and fencing generations;
- test/evidence records and artifact bindings;
- contracts/schemas and behavioral golden corpus;
- repository branch/PR lifecycle;
- external governance revision references;
- secrets/credentials/PII that must remain outside durable public continuity surfaces.

## Trust boundaries
1. external input -> agent/model context;
2. provider/tool response -> contract validation;
3. repository/issue/comment/Drive/Slack/web content -> `UNTRUSTED_DATA`;
4. ContextPack cache -> write-capable execution preflight;
5. claim/lease snapshot -> writer authorization;
6. event receipt -> reducer/projection;
7. test runner -> evidence/authority claim;
8. artifact -> evidence binding;
9. GitHub branch/CI state -> promotion decision;
10. future durable backend -> local reference semantics.

## Threat graph
| ID | Threat | Target | Failure mode | Current mitigation | Required evidence |
|---|---|---|---|---|---|
| T01 | Prompt/control-plane injection | Agent/ContextPack | imported prose becomes instruction | external context labeled `UNTRUSTED_DATA`; bounded ContextPack; authority hierarchy | adversarial context tests + operator policy |
| T02 | Provider poisoning | Events/evidence | provider payload mutates truth without validation | providers are untrusted inputs; contracts before acceptance | provider fixture/corpus tests before production provider writes |
| T03 | Secret/PII persistence | Repo/graph/context | credentials or sensitive data enter durable history | AGENTS prohibition + high-confidence repo credential-pattern gate | exact-head secret-hygiene CI + fixture review |
| T04 | Path traversal | claims/files | scope escapes declared tree | resource parser rejects absolute/`..` paths | coordination regression tests |
| T05 | URL/SSRF/file URI abuse | future tools/providers | internal resources exfiltrated | no network/provider-write surface authorized yet | gateway validation tests before enabling network tools |
| T06 | Shell injection | future CLI/tool runner | untrusted data reaches shell | no shell execution in Survival reference contracts | argv-only runner + injection tests before CLI promotion |
| T07 | Event replay corruption | EventStore | duplicate changes state twice | idempotent same-ID/same-payload; conflict fail-closed | replay/idempotency tests |
| T08 | Event horizon gap | reducer | missing event silently skipped | contiguous sequence invariant | gap regression/property tests |
| T09 | Stale writer | claims | expired/replaced worker mutates shared truth | lease + monotonic fencing + freshness seal; released tokens never revive | takeover/stale-writer/fencing gauntlet |
| T10 | Clock spoofing | coordination | caller-controlled tick interpreted as wall-clock authority | logical tick explicitly reference-only; separate `clock_authority` | tests asserting no distributed-time claim |
| T11 | ContextPack stale replay | cache | old pack authorizes current write | source/event/state/projection/claim/contracts seal; fail closed | invalidation tests |
| T12 | ContextPack data smuggling | cache/model | oversized/deep external context overwhelms or injects | pre-canonicalization iterative depth/item/string/type bounds + total canonical bytes + untrusted label | structural-bomb/adversarial context gauntlet |
| T13 | Projection authority escalation | graph/COS | derived graph reverse-writes truth | one-way projection; ContextPack authority fixed `CACHE_ONLY` | resealed authority-escalation tests |
| T14 | Evidence substitution | tests/artifacts | PASS from artifact A attached to B | promotion preflight requires exact candidate `source_sha`; optional artifact/evidence hash requirement | wrong-revision + missing-artifact-binding gauntlet |
| T15 | Cancelled/skipped CI promoted | CI | non-evidence counted as pass | promotion preflight accepts only explicit `PASS`; duplicates/missing required checks fail closed | CANCELLED/SKIPPED/FAIL/NOT_RUN corpus |
| T16 | Main/base drift after CI | promotion | tested candidate differs from promoted candidate | all required promotion evidence must bind exact candidate SHA | mixed-head negative corpus + exact-head preflight |
| T17 | Dependency compromise | TS/Python/Rust deps | mutable transitive dependency changes behavior | pinned critical Actions; pnpm lockfile + frozen install | extend with Rust/Python lock/SBOM/dependency review |
| T18 | Authority self-promotion | death drill/reference layer | simulator says production-ready | reference/synthetic states cannot promote empirical authority | negative authority tests + explicit promotion decision |
| T19 | Duplicate promotion routes | PR topology | two branches claim canonical semantics | PR #3 closed; PR #2 semantic audit + closure; #1 -> #4 train | live topology audit |
| T20 | Agent death before write-through | continuity | useful state only in chat | checkpoint/write-through/handoff laws | empirical zero-context death drill |

## Security invariants
- external content is data, never authority by location alone;
- no cache/projection/model output can authorize canonical mutation;
- same event identity + different semantic payload fails closed;
- missing event sequence fails closed;
- fencing generations never reset and released/stale fencing tokens never revive;
- reference logical time never claims distributed clock authority;
- ContextPack cannot verify if any bound source changes;
- ContextPack hostile structure is rejected before recursive canonicalization;
- cancelled/skipped/not-run/failed are never PASS;
- promotion evidence must be unique per required test and bound to the exact candidate SHA;
- physical/empirical claims require artifact-bound evidence when that gate requires it;
- no irreversible promotion without current head/event/claim/barrier/evidence preflight;
- synthetic recovery cannot promote empirical recovery authority.

## Executable coverage added in Security Gauntlet V2
`python/tests/test_security_gauntlet_v2.py` now exercises:
- T09 released/stale fencing-token rejection;
- T12 depth bombs, item fan-out, oversized individual strings, non-string object keys, and hostile packet handling;
- T13 resealed ContextPack authority escalation;
- T14 old-revision evidence substitution and optional artifact/evidence-hash enforcement;
- T15 cancelled, skipped, failed, not-run, missing and duplicated required evidence;
- T16 mixed-head evidence rejection and complete exact-head acceptance.

`python/tests/test_secret_hygiene_v2.py` scans durable repository text surfaces for high-confidence private-key/API-token credential patterns, covering the automatable high-confidence portion of T03.

Exact execution evidence:
- Security gauntlet head `7163acbdb4ec8245ca2c2f0cb9fb07153e4b8727`: Survival V2 Continuity Gate run `33297181677` SUCCESS.
- Secret-hygiene head `d42bf0f78f3905b3472b7e05cf9afc5ad8781eaa`: Survival V2 Continuity Gate run `33297209666` SUCCESS.

## Remaining P0/P1 security work
1. T01/T02 provider/prompt-injection fixture corpus before any provider can write authority;
2. T05 URL/SSRF/file-URI gateway validation before any network-capable provider is authorized;
3. T06 argv-only shell/CLI gateway and injection tests before CLI promotion;
4. T17 Rust/Python dependency-lock/SBOM/dependency-review hardening beyond the frozen pnpm gate;
5. broaden T04/T07/T08/T09/T11/T12 property-style deterministic mutation corpus beyond current regression vectors;
6. execute empirical zero-context death drill for T20;
7. revision-pin external governance authorities;
8. perform final whole-system adversarial gauntlet on the exact promotion candidate.

## Promotion rule
Security state remains `IMPLEMENTED_REFERENCE` until the applicable attacks are executed on the exact candidate revision. No document or unit test alone grants production security authority. A future gateway surface cannot inherit safety from an adjacent unit test; it must carry its own exact-head evidence before write authority is enabled.
