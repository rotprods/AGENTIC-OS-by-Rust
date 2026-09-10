# STATE — Agent Survival V2

Authority: human-readable projection only. Live GitHub lifecycle + machine-readable state/checkpoints + physically verified executed checkout + exact-SHA CI + revision-pinned governance evidence outrank this file when stale.

## Current phase
`F1_VNEXT_CONTRACT_KERNEL + SURVIVAL_V2_SHADOW / CP17_NODE24_ACTIONS_AND_EXACT_HEAD_PROVENANCE`

Whole-system authority remains `IMPLEMENTED / SHADOW_ONLY`. Event watermark remains `0`.

## Canonical topology
- PR #1: F1 base authority `015abe49353f744269d10cec7f7d3778a46e963c` — **VERIFY LIVE BEFORE USE**.
- PR #4: sole Survival V2 promotion route, branch `feat/graph-refactor-v2-survival`.
- CP16 is integrated at canonical GitHub-verified merge `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7` — **VERIFY LIVE BEFORE USE**.
- PR #30: isolated CP17 T17/provenance candidate lane from `a1fffa713...`; its lifecycle must always be fetched live. It is not encoded as an unconditional merge action.
- GGEV2 PR #18 was reconstructed as based on pre-CP16 `d19009055...` and `mergeable=false`; its exact-source snapshot is stale/rebuild-required before any semantic integration.

## CP17 T17 defects closed in the candidate lane
1. **Node20 runtime drift under immutable Action pins** — SHA-pinned checkout/setup-python/setup-node/upload-artifact commits targeted deprecated Node20 and hosted runners silently forced Node24. All permanent workflows now use audited exact Node24-native first-party Action commits.
2. **Parity runtime/dependency drift** — F1 Parity now pins Ubuntu 24.04, Python 3.13.15 + hash-locked `requirements/ci.lock`, Node 24.20.0 and pnpm 10.15.0 + frozen lockfile.
3. **Continuity provenance drift** — Continuity now matches the provenance declared by its lock: Ubuntu 24.04 + Python 3.12.3 exact + isolated hash-locked binary-only closure.
4. **Action inventory parser blind spot** — static policy now parses both `- uses:` and named-step `uses:` YAML forms, so setup-node/upload-artifact and other named Actions can no longer escape immutable-pin enforcement.
5. **P0 synthetic merge-ref false authority** — PR workflow metadata `head_sha` did not prove the checkout under test. Default checkout used `refs/pull/<n>/merge`. Every PR qualification gate now explicitly checks out `${{ github.event.pull_request.head.sha || github.sha }}` and asserts `git rev-parse HEAD` equals that candidate before testing.
6. **CI evidence source substitution** — CP13 evidence and artifact identity now bind to the explicit executed `CANDIDATE_SHA`, not the synthetic `GITHUB_SHA` merge ref.

## Historical CI authority correction
Prior PR-triggered gates that lacked explicit candidate checkout are compatibility/merge-ref evidence, not physical exact-head proof. In particular, CP16 pre-merge PR runs must not be cited as exact candidate-head authority.

CP16 nevertheless remains exactly qualified because the canonical post-merge **push** runs physically executed canonical `a1fffa71331b1ba24e95bf9be4184b8ca219c9c7` and all six completed successfully:
- Continuity `34502139152`
- Rust `34502139238`
- Parity `34502139197`
- Supply `34502139222`
- Property `34502139118`
- CLI `34502139133`

All run/SHA values are **VERIFY LIVE BEFORE USE**.

## CP17 code-candidate evidence
Frozen pre-persistence code candidate `ee695f8e14538faf1b354a637891f80cb0cd98c0` passed all six PR gates with explicit physical candidate checkout verification:
- Continuity `34503887361`
- Rust `34503887335`
- Parity `34503887336`
- Supply `34503887274`
- Property `34503887429`
- CLI `34503887378`

These runs verify the implemented code delta but become ancestor evidence once CP17 state/checkpoint/evidence persistence advances the lane head. Final persisted CP17 head requires a fresh six-gate qualification before integration.

## Current supply-chain invariants
- Every permanent external Action reference is a 40-hex commit SHA.
- Approved Survival first-party JS Actions are exact audited Node24-native pins:
  - checkout `3d3c42e5aac5ba805825da76410c181273ba90b1`
  - setup-python `5fda3b95a4ea91299a34e894583c3862153e4b97`
  - setup-node `820762786026740c76f36085b0efc47a31fe5020`
  - upload-artifact `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`
- Known Node20 first-party pins fail closed.
- Every checkout keeps `persist-credentials:false`.
- Permanent workflows use `ubuntu-24.04`; qualification runtimes are explicit where relevant.
- PR qualification requires `executed git HEAD == explicit candidate SHA`.
- CP13 `source_sha` means executed candidate source, not synthetic merge-ref identity.
- TypeScript native CycloneDX remains explicitly deferred; exact dependency tree + licenses + audit are replacement evidence. No pnpm major upgrade is justified solely for SBOM format.

## Checkpoint authority model
Current checkpoint binding remains CP16 semantics: the latest checkpoint seals the state immediately before pointer advancement. Verification rewinds only `latest_checkpoint_id` to the checkpoint parent; unrelated state drift remains cryptographically bound. Historical lineage is structurally checked without silently recertifying intentionally failed evidence.

## Governance / promotion truth
- CP01/CP02/CP03 remain `CANDIDATE_PINNED`, not promotion authority.
- The promotion observer is non-authoritative by design. CP16 canonical observation remained `promotion_authority=false` / `BLOCKED`; external enforcement was not active.
- Required checks, PR-only writes, no-force-push, no-deletion, admin enforcement and signed-head enforcement remain external hard blockers until independently observed active.
- Governance pins recorded by earlier checkpoints are **VERIFY LIVE BEFORE USE** before promotion decisions.

## Empirical / executor boundary
This session inherited predecessor context and cannot qualify the genuine fresh-successor death drill. Durable writer, network executor, process executor and multi-host authority remain unqualified. Event watermark stays `0`.

## Hard blockers
1. Genuine fresh-runtime empirical zero-context successor drill.
2. CP01/CP02/CP03 promotion qualification beyond exact candidate locators.
3. GitHub promotion enforcement + signed-head enforcement independently active.
4. Durable accepted-event writer qualification after the hard gates above; watermark remains `0` until then.
5. Real network/process executors and multi-host authority remain unqualified/deferred.

## Next safe frontier
1. Reconstruct PR #30 and PR #4 live. If CP17 is merged and the resulting canonical head has fresh exact-checkout six-gate qualification, open an isolated CP18 deterministic Property/Fuzz lane; if CP17 is not canonical, do not start CP18.
2. CP18 should target remaining generative gaps only: URL normalization/SSRF and argv/process-policy deterministic campaigns, while running the existing replay/checkpoint/fencing property corpora under the dedicated Property Union gate.
3. Configure/observe external GitHub promotion enforcement and complete CP01/CP02/CP03 governance without converting locator knowledge into authority.
4. Accept empirical recovery only from a genuinely fresh independent runtime and raw verifier evidence.
5. Only after governance + enforcement + empirical gates close, run the final whole-system gauntlet and then qualify the simplest single-host durable accepted-event writer.

Lifecycle rule: CP16 is consumed. PR #30 lifecycle is external live state. If PR #30 is already merged, never replay its integration; if it is open, candidate green is not canonical authority; if head/base changed, requalify.
