# HANDOFF — GRAPH-REFACTOR-V2 / Agent Survival CP17

Authority: zero-context recovery projection. **VERIFY LIVE TRUTH BEFORE EXECUTION.** It never outranks live GitHub, machine state/checkpoints, physically verified executed checkout, exact-SHA CI or revision-pinned governance evidence.

## Identity
- project: `rot://project/agentic-os`
- objective: `rot://objective/agentic-os/survival-v2-cp17-node24-actions-provenance`
- workstream: `rot://workstream/agentic-os/graph-refactor-v2-survival`
- expected checkpoint after seal: `state/checkpoints/cp17-node24-actions-provenance-20260910.json`
- canonical Survival branch/PR: `feat/graph-refactor-v2-survival` / PR #4
- CP17 candidate lane: `feat/cp17-node24-actions-provenance-20260910` / PR #30
- CP17 base at creation: `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7`
- F1 semantic source: `015abe49353f744269d10cec7f7d3778a46e963c`
- event watermark: `0`
- whole-system authority: `IMPLEMENTED / SHADOW_ONLY`

Every SHA, PR lifecycle and external governance revision above is **VERIFY LIVE BEFORE USE**.

## Consumed transitions
- CP15 integration is consumed at `d19009055...`.
- CP16 integration is consumed at reconstructed canonical GitHub-verified merge `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7`.
- Never replay either integration because stale prose requests it.

## CP17 result
CP17 hardens T17 and CI authority without promoting runtime authority:

1. Migrates first-party JS Actions from SHA-pinned Node20-targeting revisions to exact audited Node24-native release commits.
2. Pins all permanent workflows to Ubuntu 24.04.
3. Makes Parity reproducible with Python 3.13.15 + hash-locked `requirements/ci.lock`, Node 24.20.0, pnpm 10.15.0 and frozen pnpm lock.
4. Aligns Continuity to its declared lock provenance: Python 3.12.3 / Ubuntu 24.04, isolated venv, hash-locked binary closure.
5. Fixes the static Action scanner so both named and unnamed YAML `uses:` forms are actually inspected.
6. Closes a P0 exact-head evidence bug: pull-request workflows no longer execute the default synthetic `refs/pull/*/merge`; each explicitly checks out `pull_request.head.sha || github.sha` and asserts physical HEAD equality before tests.
7. CP13 evidence now records the executed `CANDIDATE_SHA`, not synthetic merge-ref `GITHUB_SHA`.

## Historical evidence correction
Do not cite pre-CP17 PR run metadata alone as proof that the PR head itself was physically executed. The first CP17 failure proved default checkout used a synthetic merge ref.

CP16 remains qualified because its canonical **push** runs physically tested `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7`:
- Continuity `34502139152`
- Rust `34502139238`
- Parity `34502139197`
- Supply `34502139222`
- Property `34502139118`
- CLI `34502139133`

All are **VERIFY LIVE BEFORE USE**.

## CP17 code-candidate evidence
Pre-persistence candidate `ee695f8e14538faf1b354a637891f80cb0cd98c0` passed all six PR gates after the explicit checkout repair:
- Continuity `34503887361`
- Rust `34503887335`
- Parity `34503887336`
- Supply `34503887274`
- Property `34503887429`
- CLI `34503887378`

These are ancestor/code-delta evidence after persistence changes. The final CP17 head must be requalified from live metadata/logs before integration.

## CP17 lifecycle — mandatory conditional handling
**Fetch PR #30 and PR #4 live before any lifecycle action.**

- If PR #30 is OPEN: CP17 is candidate-only. Require its current head to pass Continuity/Rust/Parity/Supply/Property/CLI with explicit physical checkout equality. Do not infer authority from an older green head.
- If PR #30 is MERGED: integration is consumed. Never merge again. Reconstruct resulting PR #4 head/signature and require fresh canonical push qualification.
- If head/base changed, closed unmerged, or canonical Survival moved: stop stale write; compare semantic deltas and requalify.

## Concurrency boundary
GGEV2 PR #18 was reconstructed from `d19009055...` and `mergeable=false` after CP16. It is stale relative to CP16/CP17 Survival state. Preserve its compatible work but rebuild any exact-source-derived snapshot before semantic integration. CP17 does not rewrite that lane.

## Supply-chain authority
Approved first-party JS Action pins:
- checkout `3d3c42e5aac5ba805825da76410c181273ba90b1`
- setup-python `5fda3b95a4ea91299a34e894583c3862153e4b97`
- setup-node `820762786026740c76f36085b0efc47a31fe5020`
- upload-artifact `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`

The policy also requires every external Action to be a 40-hex SHA, known Node20 pins absent, checkout credentials non-persistent, Ubuntu 24.04 explicit and permanent workflows without `contents: write`.

TypeScript native CycloneDX remains explicitly deferred because the native path would require a pnpm major solely for SBOM format. TypeScript audit + exact dependency tree + license evidence remains the replacement evidence.

## Governance / empirical boundaries
- CP01/CP02/CP03 remain `CANDIDATE_PINNED`, promotion-blocked.
- Promotion observer success means the observer executed; it never grants authority. External GitHub enforcement remained absent at the CP16 observation.
- This inherited-context session cannot qualify the independent fresh-successor empirical drill.
- Durable writer, real network/process executors and multi-host authority remain unqualified; event watermark is `0`.

## Resume recipe
1. Fetch PR #4 and PR #30 live plus all competing open PRs. Treat every expected SHA here as **VERIFY LIVE BEFORE USE**.
2. Load `state/project_state.json`; dynamically resolve latest checkpoint; validate schema, document hash, pre-pointer state binding and lineage topology.
3. Read `STATE.md`, `TASKS.md`, this handoff and CP17 evidence. Reconcile any contradiction against live/machine authority.
4. For PR checks, require physical `git HEAD == CANDIDATE_SHA`; run metadata `head_sha` alone is insufficient.
5. If PR #30 is already merged, never replay it; inspect the new canonical SHA/signature and fresh push gates instead.
6. If CP17 is canonical and six-gate requalified, the next executable wave is isolated CP18 deterministic Property/Fuzz for URL normalization/SSRF + argv/process policy, plus expansion of the dedicated Property Union to execute the full deterministic corpus.
7. Preserve external hard blockers: CP governance, GitHub promotion/signed-head enforcement and genuinely independent empirical recovery.
8. Keep event watermark `0`; do not qualify durable writer or real executors prematurely.
9. Refresh/rebuild GGEV2 PR #18 exact-source snapshots before semantic integration if that lane is resumed.
