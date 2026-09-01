# Survival V2 Security Gateways — CP10 Reference Boundary

Status: `IMPLEMENTED / SHADOW_ONLY` until exact-candidate qualification and explicit promotion.

This slice closes reference-level implementation gaps for T01/T02, T05 and T06 without exposing a network client, DNS resolver, provider executor, shell, or subprocess runtime.

## Authority ceiling

These primitives are validators and planners only.

They MUST NOT be interpreted as:
- production network authority;
- a qualified shell/process executor;
- proof that arbitrary provider output is safe to execute;
- cross-runtime canonical contract parity;
- empirical recovery evidence.

The existing event watermark and accepted-event authority are unchanged.

## T01/T02 — untrusted external content

`seal_untrusted_content()`:
- preserves external content as opaque data;
- assigns `UNTRUSTED_DATA`;
- sets instruction, evidence and promotion authority to `false`;
- hashes the original UTF-8 payload;
- enforces a byte bound;
- never parses payload text into commands, evidence or authority.

The deterministic corpus in `fixtures/security/untrusted-content-v1.json` includes prompt-role injection, fake evidence, fake revisions, tool-call-shaped text, secret-exfiltration requests, projection escalation and Unicode-confusable content.

This proves only the envelope boundary. Any future provider/tool adapter must consume the envelope without adding an interpretation path that promotes payload text into instructions or authority.

## T05 — network / URL planning boundary

`plan_network_request()`:
- accepts only explicitly allowed `http`/`https` schemes, defaulting to HTTPS only;
- supports read-only `GET`/`HEAD` plans;
- rejects URL-embedded credentials;
- rejects fragments;
- rejects localhost and non-global IP literals;
- supports an exact hostname allowlist plus explicit deny domains;
- enforces an explicit port allowlist, defaulting to 443;
- requires an explicit trust classification and provenance;
- binds redirect count, timeout and response-size limits;
- sets redirect policy to `REVALIDATE_EACH_HOP`;
- requires post-resolution address validation;
- keeps the raw URL out of dataclass `repr` and omits path/query from the audit record.

`validate_resolved_addresses()` rejects every non-global resolved address. A future network executor MUST call it after DNS resolution and again after every redirect. The executor must connect to the validated/pinned resolved address rather than perform an unchecked second resolution. Static URL parsing alone does not claim DNS-rebinding or DNS TOCTOU safety.

No request is performed by this module.

## T06 — shell/process planning boundary

`plan_process_invocation()`:
- requires an explicit executable allowlist;
- rejects shell interpreters;
- uses argv tokens only and sets `shell=false`;
- bounds argv count/bytes, timeout and output bytes;
- bounds cwd beneath an explicit root;
- allowlists environment keys;
- never retains environment values in the returned audit plan;
- keeps raw argv out of dataclass `repr` and records only argv count + hash in the audit record;
- preserves shell metacharacters as literal argv tokens rather than interpreting them.

This protects against implicit shell interpolation. It does not claim executable-specific argument safety. Any future executable adapter must add command-specific argument policy before execution where the target program has dangerous flags or indirection features.

No process is started by this module.

## Structured rejection surface

All rejects use `SurvivalContractError` with deterministic codes. New gateway codes are a reference security surface, not yet a Rust/TypeScript/Python shared canonical contract.

## Promotion conditions

Before these gateways can underwrite real network/process capabilities:
1. define the promoted shared contract and cross-runtime parity requirement if they become canonical;
2. bind command-specific argument policies for executable adapters;
3. bind DNS resolution + redirect revalidation into the actual HTTP executor and connect only to the validated/pinned address;
4. prove credential isolation and bounded I/O in the executor;
5. run exact-head security and continuity gates;
6. preserve evidence and authority ceiling in the checkpoint/handoff.
