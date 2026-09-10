# HANDOFF V2

> This handoff is invalid if the successor needs prior chat history.

## Identity
- project_id:
- objective_id:
- workstream_id:
- agent_id:
- session_id:
- correlation_id:

## Authority snapshot
- observed_source_sha:
- event_watermark:
- branch:
- PR:
- head_sha:
- authority_state:
- projection_hash:
- context_pack_hash:

## Scope
- files/trees touched:
- semantic contracts touched:
- claims/leases acquired:
- claims/leases released:

## Why this work exists
- North Star contribution:
- causal predecessors:
- decisions governing this work:

## Completed
- exact deliverables:
- commits:
- artifacts/hashes:

## Verification
For each test record exact status `PASS|FAIL|SKIPPED|CANCELLED|NOT_RUN`, source SHA, run ID and what the test proves/does not prove.

## Code review findings
- fixed:
- unresolved:

## Security review findings
- trust boundaries inspected:
- fixed:
- residual risks:

## Current blockers / degraded externals
- blocker:
- owner/dependency:
- unblock trigger:

## Graph delta
- nodes added/changed/superseded:
- edges added/changed/superseded:
- projections invalidated:

## Task / decision delta
- tasks completed/created/blocked:
- decisions accepted/superseded:
- refactor debt / ideas preserved:

## Next safe actions
1.
2.
3.

## Resume recipe
1. Read `AGENTS.md`, `prompts/GRAPH_REFACTOR_V2.md` and current canonical state.
2. Reconstruct live Git lifecycle/event horizon; do not trust this handoff if stale.
3. Verify active scopes/claims and applicable barriers.
4. Re-run or inspect exact evidence before claiming VERIFIED.
5. Continue only the highest-value safe task.

## NEXT_ITERATION_METAPROMPT
`VERIFY LIVE TRUTH BEFORE EXECUTION.`

Previous session summary:
- objective:
- current authority:
- verified evidence:
- blockers:
- next candidate wave:
- invalidate this packet if observed_source_sha/event_watermark/contracts/claims differ from live truth.
