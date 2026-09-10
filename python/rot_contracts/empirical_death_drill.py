from __future__ import annotations

from typing import Any

from .survival import DEFAULT_DEATH_DRILL_SLO_SECONDS, SurvivalContractError, evaluate_death_drill


REQUIRED_REPORT_FIELDS = (
    "project_id",
    "current_objective_id",
    "observed_source_sha",
    "event_watermark",
    "active_workstreams",
    "active_claims",
    "blockers",
    "verified_capabilities",
    "unverified_capabilities",
    "next_safe_actions",
)


def verify_empirical_successor_report(
    expected_state: dict[str, Any],
    submission: dict[str, Any],
    *,
    slo_seconds: float = DEFAULT_DEATH_DRILL_SLO_SECONDS,
) -> dict[str, Any]:
    """Score a report produced by a genuinely fresh successor runtime.

    This verifier does not manufacture empirical evidence. The caller must supply a report
    produced outside the predecessor context. `fresh_context_attestation` and the durable-input
    ledger make that boundary explicit and auditable rather than silently treating a synthetic
    replay as empirical qualification.
    """
    if type(submission) is not dict:
        raise SurvivalContractError("empirical death-drill submission must be object")
    if submission.get("fresh_context_attestation") is not True:
        raise SurvivalContractError("fresh successor context attestation required")
    forbidden = submission.get("forbidden_inputs")
    if type(forbidden) is not list or forbidden:
        raise SurvivalContractError("empirical drill must declare zero forbidden inputs")
    durable_inputs = submission.get("durable_inputs")
    if type(durable_inputs) is not list or not durable_inputs or not all(
        isinstance(item, str) and item for item in durable_inputs
    ):
        raise SurvivalContractError("durable_inputs must be a non-empty string list")
    elapsed = submission.get("elapsed_seconds")
    report = submission.get("reconstructed_state")
    if type(report) is not dict:
        raise SurvivalContractError("reconstructed_state must be object")
    missing = [field for field in REQUIRED_REPORT_FIELDS if field not in report]
    if missing:
        raise SurvivalContractError(f"reconstructed_state missing required fields: {','.join(missing)}")

    result = evaluate_death_drill(
        expected_state,
        report,
        elapsed_seconds=elapsed,
        slo_seconds=slo_seconds,
    )
    passed = bool(result["passed"])
    return {
        **result,
        "authority": "EMPIRICALLY_QUALIFIED" if passed else "BLOCKED",
        "fresh_context_attested": True,
        "durable_inputs": list(durable_inputs),
        "forbidden_inputs": [],
        "runtime_id": submission.get("runtime_id"),
        "session_id": submission.get("session_id"),
        "drill_id": submission.get("drill_id"),
    }
