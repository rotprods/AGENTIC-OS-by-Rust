# CP10 — Security Gateway Reference Evidence — 2026-08-31

Authority: evidence ledger entry for a SHADOW/REFERENCE wave. It does not grant production authority.

## Live truth reconstructed before mutation
- repo: `rotprods/AGENTIC-OS-by-Rust`
- active route: PR #4 `feat/graph-refactor-v2-survival` on PR #1
- F1 base: `015abe49353f744269d10cec7f7d3778a46e963c`
- pre-wave head: `f56f428a156b5737c22a889d0ca236854b3da48e`
- CP9 durable watermark: `0`
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`
- empirical verifier: VERIFIED
- real fresh-successor empirical capability: UNVERIFIED

## Governance search result
The pinned constitutional repository `rotprods/rot.knowledge` was searched for CP01, CP02 and CP03 and returned no matches. Broader owner search found unrelated uses of `CP01`; `rotprods/Clever-Agent` was inspected and its CP01 is `Forensic upstream inventory` for objective `CLEVER-JARVIS-001`. That semantic collision was explicitly rejected. CP01/CP02/CP03 remain `UNRESOLVED / BLOCKED_EXTERNAL`.

## Implementation commits
1. `580fa358d9813f826215ab244ef589e5fc894c95` — initial fail-closed T01/T02/T05/T06 reference gateway implementation.
2. `6992478ada66339470e934052b740cba7db0f2b1` — adversarial hardening after gauntlet found raw URL/query and raw argv audit leakage; added redaction, argv hashing, deny-domain policy and explicit port allowlist.

## Implemented contracts
### T01/T02
External content is preserved byte-for-byte as data, hashed, bounded and marked `UNTRUSTED_DATA`. It cannot set instruction, evidence or promotion authority. Deterministic corpus covers prompt-role injection, fake system text, fake evidence/revisions, tool-call-shaped payloads, secret-exfiltration instructions, projection escalation and Unicode-confusable text.

### T05
The module produces a request plan only. It rejects disallowed schemes/methods, URL credentials/fragments, localhost, non-global literal/resolved IPs, denied hosts and unapproved ports; requires explicit trust/provenance; bounds redirects/timeouts/response size; and requires DNS/redirect address revalidation. A future executor must connect to the already validated address to avoid unchecked DNS re-resolution.

### T06
The module produces a process plan only. It requires an executable allowlist, hard-denies shell interpreters, fixes `shell=false`, bounds argv/cwd/env/time/output, and emits structured errors. Audit output contains argv count/hash, not raw args or environment values. Executable-specific flag policy remains a prerequisite for real execution.

## Exact candidate qualification
Source SHA `6992478ada66339470e934052b740cba7db0f2b1`:
- Survival V2 Continuity Gate — run `33439991898` — PASS.
- F1 Rust Contract Kernel — run `33439991928` — PASS.
- F1 Cross-Language Parity — run `33439991874` — PASS.

## Empirical boundary
NOT RUN. This runtime inherited predecessor/chat context and cannot truthfully attest fresh zero-context independence. No synthetic submission was manufactured.

## Authority after CP10
- T01/T02 envelope/corpus: `VERIFIED_REFERENCE`.
- T05 network planner: `VERIFIED_REFERENCE`.
- T06 process planner: `VERIFIED_REFERENCE`.
- network executor: `UNVERIFIED`.
- process executor: `UNVERIFIED`.
- empirical zero-context recovery: `UNVERIFIED`.
- CP01/CP02/CP03: `BLOCKED_EXTERNAL`.
- durable accepted-event writer: `UNQUALIFIED`.
- whole system: `IMPLEMENTED / SHADOW_ONLY`.
- event watermark: `0`.
- distributed/multi-host authority: `DEFERRED`.

## Promotion-assurance observations
The active Survival branch reports branch protection disabled and required status-check enforcement off. Observed commits are unsigned. These are T17/promotion-assurance risks, not evidence of a security failure in the CP10 reference primitives.

## Graph delta
- `SecurityGatewayReference --IMPLEMENTS_REFERENCE--> UntrustedExternalContentEnvelope`
- `SecurityGatewayReference --IMPLEMENTS_REFERENCE--> NetworkPolicyPlanner`
- `SecurityGatewayReference --IMPLEMENTS_REFERENCE--> ProcessPolicyPlanner`
- `SecurityGatewayTests --TESTS--> T01/T02/T05/T06 reference capabilities`
- `UntrustedContentCorpus --ADVERSARIAL_CORPUS_FOR--> T01/T02`
- `NetworkExecutor --REMAINS--> UNVERIFIED`
- `ProcessExecutor --REMAINS--> UNVERIFIED`
- `EmpiricalRun --NOT_EXECUTED--> EmpiricalZeroContextDeathDrill`
- `CP01/CP02/CP03 --BLOCKS--> GovernanceReady`
- `AcceptedEventAuthority --REMAINS--> UNQUALIFIED@watermark0`

## Next safe action
Complete T17 Rust/Python dependency reproducibility, vulnerability/SBOM/provenance assurance and broaden the deterministic property/fuzz corpus. This is executable without fabricating governance or empirical evidence and without enabling dangerous I/O.
