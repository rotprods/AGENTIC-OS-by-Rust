from __future__ import annotations

import time
from typing import Any

from .canonical_json import hash_canonical
from .survival import evaluate_death_drill, verify_checkpoint
from .survival_graph import build_survival_projection
from .survival_store import recover_from_bundle


REPORT_FIELDS = (
    "project_id", "current_objective_id", "observed_source_sha", "event_watermark",
    "active_workstreams", "active_claims", "blockers", "verified_capabilities",
    "unverified_capabilities", "next_safe_actions",
)


def run_synthetic_death_drill(
    recovery_bundle: dict[str, Any], *, expected_state: dict[str, Any],
    checkpoint: dict[str, Any] | None = None, slo_seconds: float = 300.0,
) -> dict[str, Any]:
    """Recover after simulated agent/store death and score state + graph parity.

    `expected_state` is the external test oracle retained by the gauntlet, not input available
    to the recovered runtime. Recovery itself uses only the sealed recovery bundle and optional
    checkpoint. This distinction prevents the drill from proving itself by reading the answer.
    """
    expected_state_hash = hash_canonical(expected_state)
    expected_projection = build_survival_projection(expected_state, checkpoint=checkpoint)

    started = time.perf_counter()
    recovered = recover_from_bundle(recovery_bundle)
    if checkpoint is not None:
        verify_checkpoint(checkpoint, state=recovered)
    rebuilt_projection = build_survival_projection(recovered, checkpoint=checkpoint)
    report = {field: recovered[field] for field in REPORT_FIELDS}
    elapsed = time.perf_counter() - started

    truth = evaluate_death_drill(
        expected_state,
        report,
        elapsed_seconds=elapsed,
        slo_seconds=slo_seconds,
    )
    state_parity = hash_canonical(recovered) == expected_state_hash
    graph_parity = rebuilt_projection["projection_hash"] == expected_projection["projection_hash"]
    passed = bool(truth["passed"] and state_parity and graph_parity)
    return {
        "passed": passed,
        "authority": "VERIFIED_SYNTHETIC_RECOVERY" if passed else "BLOCKED",
        "state_parity": state_parity,
        "graph_parity": graph_parity,
        "elapsed_seconds": elapsed,
        "slo_seconds": slo_seconds,
        "continuity_defect": not passed,
        "mismatches": truth["mismatches"],
        "recovered_state_hash": hash_canonical(recovered),
        "recovered_projection_hash": rebuilt_projection["projection_hash"],
        "event_watermark": recovered["event_watermark"],
    }
