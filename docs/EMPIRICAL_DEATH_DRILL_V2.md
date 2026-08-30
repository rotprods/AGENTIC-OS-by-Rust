# Empirical Agent Death Drill V2

Status: `READY_FOR_EMPIRICAL_EXECUTION` as a protocol. This document does **not** constitute empirical qualification.

## Purpose

Prove that a genuinely fresh successor runtime can reconstruct the bounded operational truth of Agentic OS using only durable repository surfaces, without predecessor chat memory, hidden scratchpads, private chain-of-thought, copied answers, or an oracle containing the expected result.

The synthetic recovery harness proves deterministic software behavior. This drill proves operational survivability across an actual context death boundary. The two evidence classes are intentionally distinct.

## Hard qualification rule

`EMPIRICALLY_QUALIFIED` may be recorded only after a real fresh successor session produces a submission that passes `verify_empirical_successor_report` within the 300 second SLO. Unit tests, synthetic replays, predecessor-generated reports, or reports whose input provenance cannot be audited are insufficient.

## Roles

### Predecessor / controller

The controller freezes the drill target at an exact Git commit SHA, records the approved durable-input allowlist, starts the timer, gives the successor only the minimal bootstrap instruction, receives the successor submission, and evaluates it against the expected canonical state.

The controller must not give the successor the expected reconstructed values.

### Fresh successor

The successor must begin in a new session/runtime that has no access to the predecessor conversation or hidden memory. It may inspect only the explicitly allowed durable surfaces.

## Approved durable surfaces

A drill SHOULD start with the smallest sufficient set and record every surface actually read. The default bootstrap set is:

- `AGENTS.md`
- `STATE.md`
- `TASKS.md`
- `HANDOFF.md` when present and current
- `state/project_state.json`
- the checkpoint referenced by `latest_checkpoint_id`
- revision-pinned evidence explicitly referenced by those surfaces
- live GitHub PR/head/check-run metadata when the drill prompt authorizes GitHub reads

The successor must report the exact `durable_inputs` it consumed. Additional repository files are allowed only when they are discovered through the durable continuity chain and are recorded in that ledger.

## Forbidden inputs

The successor MUST NOT consume:

- predecessor chat transcript;
- predecessor private scratchpad or chain-of-thought;
- a controller-supplied copy of expected state values;
- hidden user/session memory containing the answer;
- an unrecorded side channel from the predecessor;
- a precomputed drill solution.

The submission field `forbidden_inputs` MUST be an empty list. `fresh_context_attestation` MUST be `true`.

## Timer boundary

Start the timer when the fresh successor receives the repository/ref plus the drill instruction and durable-input policy. Stop the timer when the complete submission is emitted.

Default SLO: `<= 300 seconds`.

Do not subtract tool latency or reading time. Those are part of practical recovery cost.

## Required reconstruction

The successor must reconstruct, without being given the answers:

- `project_id`
- `current_objective_id`
- `observed_source_sha`
- `event_watermark`
- `active_workstreams`
- `active_claims`
- `blockers`
- `verified_capabilities`
- `unverified_capabilities`
- `next_safe_actions`

These fields are evaluated against the controller's canonical expected state using the same strict semantics as the synthetic death-drill evaluator.

## Submission contract

The successor emits one JSON object with at least:

```json
{
  "drill_id": "rot://drill/agentic-os/zero-context/<id>",
  "runtime_id": "<runtime identifier>",
  "session_id": "<fresh session identifier>",
  "fresh_context_attestation": true,
  "durable_inputs": ["AGENTS.md", "state/project_state.json"],
  "forbidden_inputs": [],
  "elapsed_seconds": 0.0,
  "reconstructed_state": {
    "project_id": "...",
    "current_objective_id": "...",
    "observed_source_sha": "...",
    "event_watermark": 0,
    "active_workstreams": [],
    "active_claims": [],
    "blockers": [],
    "verified_capabilities": [],
    "unverified_capabilities": [],
    "next_safe_actions": []
  }
}
```

A production execution SHOULD additionally preserve the frozen target SHA, start/end timestamps, model/runtime version where available, controller identity, and a hash of the submission as evidence metadata.

## Controller procedure

1. Read live PR #4 and freeze the exact branch head for the drill.
2. Confirm Continuity, Rust and parity gates are green for that SHA.
3. Read `state/project_state.json`; resolve its `latest_checkpoint_id` to the exact checkpoint file.
4. Record the canonical expected state privately in the controller evidence bundle. Do not send it to the successor.
5. Create a genuinely new runtime/session with predecessor conversation memory disabled/unavailable.
6. Send only: repository identity, frozen ref, the drill instruction, the durable-input policy, and the output contract.
7. Start the timer at delivery.
8. Receive the successor JSON submission and stop the timer.
9. Preserve the raw submission unchanged.
10. Run `verify_empirical_successor_report(expected_state, submission)`.
11. If any state field differs, provenance is invalid, forbidden input is declared, fresh-context attestation is absent, or elapsed time exceeds 300 seconds: result is `BLOCKED`.
12. Only a passing independently produced submission may clear `death-drill-not-empirically-executed` and promote the specific capability `empirical-zero-context-death-drill` to verified/empirically-qualified evidence.
13. Reconcile `state/project_state.json`, checkpoint, `STATE.md`, `TASKS.md`, `HANDOFF.md`, and evidence ledger after the result; then re-run exact-head CI.

## Minimal successor instruction

The controller may provide the following semantic instruction without revealing expected values:

> You are the successor after total predecessor context loss. Using only the authorized durable repository surfaces at the frozen ref, reconstruct the required operational state fields, record every durable input you consumed, declare any forbidden input exposure, and return the submission JSON defined by `docs/EMPIRICAL_DEATH_DRILL_V2.md`. Do not infer success from prose alone; resolve conflicts using repository authority rules and live revision-pinned evidence.

## Pass criteria

All are mandatory:

- genuinely fresh successor context;
- auditable durable-input ledger;
- zero forbidden inputs;
- complete required report;
- exact reconstruction under canonical comparison;
- elapsed time `<= 300s`;
- raw submission preserved as immutable evidence;
- verifier returns `passed: true` and `authority: EMPIRICALLY_QUALIFIED`;
- controller does not discover evidence contamination after the run.

## Failure semantics

A failure is useful evidence. Preserve it. Classify mismatches, recovery latency, missing surfaces, stale projections, ambiguous authority, or tool-access failures as continuity defects and feed them back into the graph/refactor backlog. Do not edit the failed submission to make it pass.

## Current status

The empirical verifier and its unit/adversarial contract tests may be `VERIFIED` independently. The actual death-drill capability remains `UNVERIFIED` until a real fresh successor session executes this protocol.
