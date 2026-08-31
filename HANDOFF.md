# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP10

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** This packet invalidates on branch/head/event/claim/contract/governance drift.

## Identity
- project: `rot://project/agentic-os`
- objective: `rot://objective/agentic-os/survival-v2-cp10-security-gateways-reference`
- workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- checkpoint: `state/checkpoints/cp10-security-gateways-reference-20260831.json`
- branch: `feat/graph-refactor-v2-survival`
- active promotion PR: #4, stacked on PR #1
- F1 base: `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0`
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`

## CP10 implemented
At implementation candidate `6992478ada66339470e934052b740cba7db0f2b1`:
- Continuity `33439991898`: PASS.
- Rust `33439991928`: PASS.
- Cross-Language Parity `33439991874`: PASS.

New reference surfaces:
- `python/rot_contracts/security_gateways.py`
- `python/tests/test_security_gateways_v2.py`
- `fixtures/security/untrusted-content-v1.json`
- `docs/SECURITY_GATEWAYS_SURVIVAL_V2.md`

T01/T02 external content is sealed as opaque non-authoritative data. T05 network planning fails closed on schemes, credentials, fragments, trust/provenance, hosts, ports, non-global addresses and bounded redirect/time/size policy; resolved addresses must be revalidated. T06 process planning rejects shells/unlisted executables, enforces cwd/env/time/output bounds and returns argv-only `shell=false` plans.

The gauntlet caught audit leakage in the first implementation: raw URL/query and raw argv could be represented in logs. The follow-up hardening removed them from repr/audit surfaces, added argv hashing, deny-domain policy and explicit port policy before CP10 was sealed.

**No network request, DNS resolver, provider writer, shell or subprocess executor is authorized by CP10.** Real executors remain UNVERIFIED.

## Empirical boundary
This runtime inherited predecessor/chat context. It therefore did **not** qualify as a fresh independent successor and did not run a fake empirical drill. The verifier/measurement harness remains VERIFIED; the real `empirical-zero-context-death-drill` capability remains UNVERIFIED.

## Governance boundary
- `rot.knowledge/main`: pinned `621550ddf725c0c3d1e41540ee878be124dfe871`.
- `COS2`: pinned `3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83`.
- CP01/CP02/CP03: `UNRESOLVED / BLOCKED_EXTERNAL`.
- CP10 searches found no CP01/02/03 matches in the pinned constitutional repository.
- A broader owner search surfaced `Clever-Agent` CP01, but inspection proved it means `Forensic upstream inventory` for a different objective. It is a nominal collision, not authority.

## Concurrency reconciliation
The active branch stayed at the expected head during both semantic writes; optimistic fast-forward updates succeeded without force. The old `state/session_identity_v2.json` still advertises a 2026-08-29 session as ACTIVE, but there is no corresponding recent heartbeat/completion trail; treat it as a stale projection, not live ownership. CP10 used append-only session events rather than overwriting that pointer.

## Remaining hard blockers
1. CP01/CP02/CP03 authoritative locators.
2. Real independent empirical zero-context successor run.
3. T17 + broader deterministic property/fuzz assurance + final exact-candidate gauntlet.
4. Durable accepted-event authority. Watermark remains 0.

## Promotion-assurance risks
- Active branch protection/status-check enforcement is currently disabled.
- Observed commits are unsigned.
- Future HTTP execution must connect to the validated/pinned resolved address and revalidate each redirect.
- Future process execution requires executable-specific argument policy.

## Resume recipe
1. Read `AGENTS.md`, `STATE.md`, `TASKS.md`, `HANDOFF.md`, `state/project_state.json`, the checkpoint named by `latest_checkpoint_id`, `docs/THREAT_MODEL_SURVIVAL_V2.md`, `docs/EMPIRICAL_DEATH_DRILL_V2.md`, `docs/SECURITY_GATEWAYS_SURVIVAL_V2.md`, and `governance/external-authorities.v1.json`.
2. Re-fetch PR #4 head/base, open competing PRs, active scopes and check runs. Reject stale evidence.
3. Keep Survival `SHADOW_ONLY`, event watermark `0`, network/process executors UNVERIFIED and distributed infrastructure DEFERRED.
4. If the current runtime is not genuinely fresh, do not execute or self-attest the empirical drill.
5. Do not guess CP01/02/03.
6. Default next non-conflicting workstream: T17 Rust/Python dependency assurance + deterministic property/fuzz corpus.
7. Before any promotion, require Continuity + Rust + Cross-Language Parity on the same exact final SHA plus applicable security/governance/empirical evidence.

## Next iteration
Close real uncertainty, not architecture aesthetics. Attack T17/property assurance unless a fresh empirical runtime or uniquely authoritative CP01/02/03 locator becomes available. Preserve exact-SHA evidence and fail closed on promotion.
