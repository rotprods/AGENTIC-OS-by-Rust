# CP17 — Node24 Actions + Exact-Head CI Provenance — 2026-09-10

Authority: durable evidence only. This document does not promote whole-system authority. Live GitHub lifecycle, `state/project_state.json`, the dynamically resolved latest checkpoint, exact executed checkout identity, exact-SHA CI and revision-pinned governance evidence outrank stale prose.

## Starting authority
- Canonical Survival PR: #4 / `feat/graph-refactor-v2-survival`.
- CP16 canonical head at CP17 branch creation: `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7`.
- F1 semantic source: `015abe49353f744269d10cec7f7d3778a46e963c`.
- Whole-system authority: `IMPLEMENTED / SHADOW_ONLY`.
- Event watermark: `0`.
- CP17 candidate PR: #30 / `feat/cp17-node24-actions-provenance-20260910`.

Every live SHA/PR lifecycle value above is **VERIFY LIVE BEFORE USE**.

## Discovery 1 — immutable Action pin != reproducible runtime
CP16 canonical runner logs showed SHA-pinned first-party JavaScript Actions targeting deprecated Node 20. GitHub-hosted runners were forcibly executing them on Node 24. The repo therefore pinned source commits but did not pin the Action runtime semantics actually executing.

Deprecated pins observed:
- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`
- `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065`
- `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`
- `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02`

Upstream releases and exact action manifests were reconstructed before mutation. Approved Node24-native immutable pins:
- `actions/checkout` v7.0.1 -> `3d3c42e5aac5ba805825da76410c181273ba90b1`
- `actions/setup-python` v7.0.0 -> `5fda3b95a4ea91299a34e894583c3862153e4b97`
- `actions/setup-node` v7.0.0 -> `820762786026740c76f36085b0efc47a31fe5020`
- `actions/upload-artifact` v7.0.1 -> `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`

The relevant major-release notes were reviewed for the input surface this repository uses. `persist-credentials:false` remains mandatory. No unrelated Action was upgraded merely for freshness.

## Discovery 2 — Parity had an unlocked runtime/dependency bypass
F1 Parity previously used:
- `ubuntu-latest`;
- the runner's implicit Python;
- direct `pip install jsonschema==4.25.1`, pinning only the top-level package while leaving interpreter and transitive closure outside the repo's hash-locked evidence;
- implicit Node/corepack/pnpm runtime selection.

Repair:
- runner pinned to `ubuntu-24.04`;
- Python pinned to `3.13.15` through the approved Node24 `setup-python` commit;
- Python closure installed from `requirements/ci.lock` with `--require-hashes` + `pip check`;
- Node pinned to `24.20.0` through the approved Node24 `setup-node` commit;
- pnpm pinned to `10.15.0` via Corepack;
- `pnpm install --frozen-lockfile`;
- `pnpm-lock.yaml` snapshotted before the test suite and compared again even if an earlier step fails.

Continuity was also aligned to the provenance already declared by `requirements/continuity.txt`: `ubuntu-24.04` + Python `3.12.3` exact + isolated venv + hash-locked binary-only closure. F1 Rust moved from `ubuntu-latest` to `ubuntu-24.04` while preserving Rust `1.88.0`, Cargo.lock identity and `--locked` behavior.

## Discovery 3 — supply-chain Action inventory parser blind spot
The previous static scanner recognized only YAML lines shaped as:

`- uses: owner/action@sha`

It missed the equally valid named-step form:

```
- name: Step
  uses: owner/action@sha
```

This meant the generic statement “all external Actions are immutable SHA-pinned” was not machine-enforced over the full workflow inventory.

Repair:
- parser accepts both named and unnamed `uses:` forms;
- regression proves `setup-node`, `upload-artifact`, `dtolnay/rust-toolchain` and `Swatinem/rust-cache` are actually observed;
- every external Action remains required to use a 40-hex commit;
- approved first-party JS Actions must equal the audited Node24-native commits;
- known deprecated Node20 commits cannot re-enter;
- every checkout must keep `persist-credentials:false`;
- all permanent workflows must use `ubuntu-24.04` and must not request `contents: write`.

## Discovery 4 — P0 exact-head evidence bug: pull_request default checkout used synthetic merge refs
The first CP17 code candidate exposed a deeper CI authority problem. On a `pull_request` event, default `actions/checkout` fetched and checked out `refs/pull/30/merge`, producing synthetic merge commit `8949da0...`, while GitHub run metadata still exposed the PR head SHA separately.

Therefore:

`workflow run metadata head_sha == candidate SHA`

did **not** prove:

`executed git HEAD == candidate SHA`.

This invalidates the historical interpretation of pre-CP17 PR runs as physical exact-head proof when their checkout was not explicit.

### Historical correction
- CP16 pre-merge PR runs are preserved as merge-ref compatibility evidence, **not exact candidate-head authority**.
- CP16 remains valid because its post-merge `push` runs physically qualified canonical `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7` on all six core gates:
  - Continuity `34502139152` — SUCCESS
  - Rust `34502139238` — SUCCESS
  - Parity `34502139197` — SUCCESS
  - Supply `34502139222` — SUCCESS
  - Property `34502139118` — SUCCESS
  - CLI `34502139133` — SUCCESS

### Repair
Every permanent workflow that can qualify a pull request now defines:

```
CANDIDATE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}
```

and checkout uses:

```
ref: ${{ env.CANDIDATE_SHA }}
persist-credentials: false
```

followed immediately by:

```
test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"
```

This is applied to Continuity, Rust, Parity, Supply, Property and Operator CLI. CP13 evidence now records `CANDIDATE_SHA`, not the synthetic `GITHUB_SHA`, and its artifact name is bound to the same candidate identity.

The static policy fails if any `pull_request` workflow loses the explicit candidate expression, checkout ref or physical HEAD assertion.

## First CP17 gauntlet failure and root-cause generalization
Initial CP17 code candidate: `8fb8f3ee3bf3fe1e0bf4b81227763c67ce362b08`.

F1 Parity failed. Two causes were separated:
1. primary: the new supply-chain policy correctly discovered the named-step `uses:` parser blind spot;
2. secondary/cascade: lockfile cleanup attempted to compare `/tmp/pnpm-lock.before` even though the snapshot step had not executed after the earlier Python-suite failure.

The fixes generalized both families rather than suppressing symptoms:
- inventory parser now covers both YAML shapes;
- pnpm lock snapshot occurs before the Python suite, so failure-path non-mutation evidence remains meaningful.

The same logs revealed the synthetic merge-ref exact-head bug, which was then repaired across all PR qualification workflows.

## CP17 code candidate qualification
Frozen code candidate: `ee695f8e14538faf1b354a637891f80cb0cd98c0`.

All six PR workflows completed successfully and, unlike historical PR gates, now physically assert the executed checkout equals `CANDIDATE_SHA`:
- Survival V2 Continuity Gate `34503887361` — SUCCESS.
- F1 Rust Contract Kernel `34503887335` — SUCCESS.
- F1 Cross-Language Parity `34503887336` — SUCCESS.
- CP13 Supply Chain Assurance `34503887274` — SUCCESS.
- Survival Store Property Union V2 `34503887429` — SUCCESS.
- Survival Operator CLI Read-Only V1 `34503887378` — SUCCESS.

Parity additionally demonstrated Python `3.13.15`, the hash-locked `ci.lock` closure, Node `24.20.0`, pnpm `10.15.0`, full Python/TypeScript parity and pnpm-lock non-mutation on the physically checked-out candidate. Supply completed exact checkout verification, lock/runtime identity, Rust advisory/source/license/bans audit, Python audit + CycloneDX, TypeScript vulnerability/dependency/license evidence, Rust CycloneDX generation/validation and the final assurance gate.

These code-candidate runs are evidence for the implemented delta. They are not the final CP17 checkpoint head once state/evidence persistence commits are added. The final persisted PR head must obtain a fresh six-gate exact-checkout qualification; those live run IDs are intentionally not embedded here because writing them back into the repository would itself create a new head.

## SBOM / dependency evidence boundary
T17 retains useful evidence rather than decorative SBOM generation:
- source identity is bound to exact candidate SHA;
- Cargo/Python/pnpm lock hashes are captured;
- toolchain versions are captured;
- Python CycloneDX and nine Rust CycloneDX documents are generated and validated;
- TypeScript `pnpm audit`, full dependency tree and license inventory are persisted in the CI artifact.

Native pnpm CycloneDX remains `DEFERRED`: the available native path requires a pnpm major upgrade and T17 has no measured requirement justifying a package-manager major solely to change SBOM format. Existing TypeScript dependency/license/audit evidence remains the explicit replacement evidence.

## Current T17 invariants
1. Run metadata alone never proves executed source identity.
2. PR qualification authority requires physical checkout equality with the explicit PR head SHA.
3. CI evidence `source_sha` must describe the executed candidate, not GitHub's synthetic merge commit.
4. Every external Action is immutable 40-hex pinned across both YAML `uses:` forms.
5. Survival first-party JS Actions use an audited exact Node24-native allowlist; known Node20 pins fail closed.
6. Permanent workflow runner generation is explicit (`ubuntu-24.04`).
7. Language/package-manager versions and lock closures are explicit where they contribute to qualification authority.
8. `persist-credentials:false` and least-privilege workflow permissions remain mandatory.

## Authority boundaries preserved
- Whole-system authority remains `IMPLEMENTED / SHADOW_ONLY`.
- Event watermark remains `0`.
- Durable accepted-event writer remains unqualified.
- Real network/process executors remain unverified; planner/validator boundaries only.
- Multi-host authority remains deferred.
- CP01/CP02/CP03 remain candidate-pinned / promotion-blocked.
- This inherited-context session cannot qualify the empirical fresh-successor death drill.
- GitHub required-check / PR-only / no-force-push / no-deletion / admin and signed-head enforcement remain external blockers until independently observed active.

## Next safe wave after CP17 becomes canonical
The remaining high-value executable reference-only work is a deterministic Property/Fuzz expansion rather than new infrastructure:
- URL normalization/SSRF property campaign over case, trailing dot, IDNA, encoded authorities, IPv4/IPv6 global-vs-nonglobal, deny-domain and port boundaries;
- argv/process-policy property campaign over token counts/lengths, NUL, cwd/env bounds, shell interpreters, metacharacter literalness and audit redaction;
- run existing replay/checkpoint/fencing/coordination/property corpora plus the new campaigns under the dedicated Property Union gate with deterministic seeds and minimized explicit regression examples.

Do not start that lane until CP17 lifecycle is reconstructed live and the CP17 canonical head, if merged, has been requalified.
