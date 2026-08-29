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
| T03 | Secret/PII persistence | Repo/graph/context | credentials or sensitive data enter durable history | AGENTS hard prohibition; no secret-bearing fixtures | secret scan + fixture review |
| T04 | Path traversal | claims/files | scope escapes declared tree | resource parser rejects absolute/`..` paths | coordination regression tests |
| T05 | URL/SSRF/file URI abuse | future tools/providers | internal resources exfiltrated | no network/provider-write surface authorized yet | gateway validation tests before enabling network tools |
| T06 | Shell injection | future CLI/tool runner | untrusted data reaches shell | no shell execution in Survival reference contracts | argv-only runner + injection tests before CLI promotion |
| T07 | Event replay corruption | EventStore | duplicate changes state twice | idempotent same-ID/same-payload; conflict fail-closed | replay/idempotency tests |
| T08 | Event horizon gap | reducer | missing event silently skipped | contiguous sequence invariant | gap regression/property tests |
| T09 | Stale writer | claims | expired/replaced worker mutates shared truth | lease + monotonic fencing + freshness seal | takeover/stale-writer tests |
| T10 | Clock spoofing | coordination | caller-controlled tick interpreted as wall-clock authority | logical tick explicitly reference-only; separate `clock_authority` | tests asserting no distributed-time claim |
| T11 | ContextPack stale replay | cache | old pack authorizes current write | source/event/state/projection/claim/contracts seal; fail closed | invalidation tests |
| T12 | ContextPack data smuggling | cache/model | oversized/deep external context overwhelms or injects | bounded depth/items/strings/serialized bytes + untrusted label | abuse-limit tests |
| T13 | Projection authority escalation | graph/COS | derived graph reverse-writes truth | one-way projection; authority=`DERIVED_PROJECTION_ONLY` | projection tamper tests |
| T14 | Evidence substitution | tests/artifacts | PASS from artifact A attached to B | revision/artifact hashes and state/checkpoint binding required | artifact/evidence binding tests as physical surfaces arrive |
| T15 | Cancelled/skipped CI promoted | CI | non-evidence counted as pass | PASS/SKIPPED/CANCELLED/NOT_RUN distinct | promotion preflight checks exact conclusion |
| T16 | Main/base drift after CI | promotion | tested candidate differs from promoted candidate | exact-head preflight required | combined-head CI before merge |
| T17 | Dependency compromise | TS/Python/Rust deps | mutable transitive dependency changes behavior | pinned critical Actions; pnpm lockfile gap explicit | frozen install + SBOM/dependency review |
| T18 | Authority self-promotion | death drill/reference layer | simulator says production-ready | reference/synthetic states cannot promote empirical authority | negative authority tests + explicit promotion decision |
| T19 | Duplicate promotion routes | PR topology | two branches claim canonical semantics | PR #3 closed; PR #2 semantic audit + closure; #1 -> #4 train | live topology audit |
| T20 | Agent death before write-through | continuity | useful state only in chat | checkpoint/write-through/handoff laws | empirical zero-context death drill |

## Security invariants
- external content is data, never authority by location alone;
- no cache/projection/model output can authorize canonical mutation;
- same event identity + different semantic payload fails closed;
- missing event sequence fails closed;
- fencing generations never reset;
- reference logical time never claims distributed clock authority;
- ContextPack cannot verify if any bound source changes;
- cancelled/skipped/not-run are never PASS;
- physical/empirical claims require artifact-bound evidence;
- no irreversible promotion without current head/event/claim/barrier/evidence preflight;
- synthetic recovery cannot promote empirical recovery authority.

## Remaining P0/P1 security work
1. add automated secret scanning and dependency/frozen-install evidence;
2. add property/fuzz tests for resource scopes, event corpus and ContextPack bounds;
3. add explicit evidence-substitution corpus when physical artifacts enter this runtime;
4. add gateway-level URL/path/shell validation before any provider/network/CLI surface becomes write-capable;
5. execute empirical zero-context death drill;
6. revision-pin external governance authorities;
7. perform final whole-system adversarial gauntlet after behavioral parity stabilizes.

## Promotion rule
Security state remains `IMPLEMENTED_REFERENCE` until the applicable attacks are executed on the exact candidate revision. No document or unit test alone grants production security authority.
