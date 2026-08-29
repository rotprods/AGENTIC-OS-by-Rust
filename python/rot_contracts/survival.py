from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
import math

from .canonical_json import hash_canonical


AUTHORITY_STATES = {
    "PROPOSED", "IMPLEMENTED", "EXECUTED", "VERIFIED",
    "EMPIRICALLY_QUALIFIED", "BLOCKED", "DEGRADED_EXTERNAL", "SUPERSEDED",
}
TEST_STATES = {"PASS", "FAIL", "SKIPPED", "CANCELLED", "NOT_RUN"}
DEFAULT_DEATH_DRILL_SLO_SECONDS = 300.0


class SurvivalContractError(ValueError):
    pass


@dataclass(frozen=True)
class FreshnessSeal:
    observed_source_sha: str
    event_watermark: int
    projection_hash: str | None = None

    def __post_init__(self) -> None:
        if not _is_git_sha(self.observed_source_sha):
            raise SurvivalContractError("observed_source_sha must be lowercase git SHA-1 hex")
        if not _strict_nonnegative_int(self.event_watermark):
            raise SurvivalContractError("event_watermark must be non-negative integer")
        if self.projection_hash is not None and not _is_hash(self.projection_hash):
            raise SurvivalContractError("projection_hash must be sha256:<64 hex>")


def assert_fresh(local: FreshnessSeal, live: FreshnessSeal) -> None:
    if local.observed_source_sha != live.observed_source_sha:
        raise SurvivalContractError("stale observed source revision")
    if local.event_watermark != live.event_watermark:
        raise SurvivalContractError("stale event watermark")
    # A known live projection cannot be silently ignored by omitting the local hash,
    # and a local projection cannot be trusted if live authority no longer exposes it.
    if local.projection_hash != live.projection_hash:
        raise SurvivalContractError("stale projection")


def reduce_events(seed: dict[str, Any], events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    state = _normalize_state(seed)
    seen: dict[str, str] = {}
    ordered = sorted((_normalize_event(event) for event in events), key=lambda event: event["sequence"])
    previous_sequence = state["event_watermark"]
    for event in ordered:
        event_id = event["event_id"]
        event_hash = hash_canonical(event)
        if event_id in seen:
            if seen[event_id] != event_hash:
                raise SurvivalContractError("same event identity with different semantic payload")
            continue
        expected_sequence = previous_sequence + 1
        if event["sequence"] != expected_sequence:
            raise SurvivalContractError(
                f"event sequence discontinuity: expected {expected_sequence}, got {event['sequence']}"
            )
        seen[event_id] = event_hash
        if event["project_id"] != state["project_id"]:
            raise SurvivalContractError("cross-project event rejected")
        _apply(state, event)
        previous_sequence = event["sequence"]
        state["event_watermark"] = previous_sequence
    return _normalize_state(state)


def build_checkpoint(
    state: dict[str, Any], *, checkpoint_id: str, agent_id: str, session_id: str,
    workstream_id: str, completed: list[str], blockers: list[str], next_actions: list[str],
    resume_recipe: list[str], parent_checkpoint_id: str | None = None,
    tests: list[dict[str, Any]] | None = None, evidence: list[str] | None = None,
    changed_paths: list[str] | None = None, decisions: list[str] | None = None,
    risks: list[str] | None = None, graph_delta: list[str] | None = None,
    task_delta: list[str] | None = None, refactor_debt: list[str] | None = None,
) -> dict[str, Any]:
    current = _normalize_state(state)
    for field, value in (
        ("checkpoint_id", checkpoint_id), ("agent_id", agent_id),
        ("session_id", session_id), ("workstream_id", workstream_id),
    ):
        _require_text_value(value, field)
    if parent_checkpoint_id is not None:
        _require_text_value(parent_checkpoint_id, "parent_checkpoint_id")

    _require_string_list(completed, "completed", allow_empty=True)
    _require_string_list(blockers, "blockers", allow_empty=True)
    _require_string_list(next_actions, "next_actions", allow_empty=False)
    _require_string_list(resume_recipe, "resume_recipe", allow_empty=False)
    _require_string_list(changed_paths or [], "changed_paths", allow_empty=True)
    _require_string_list(decisions or [], "decisions", allow_empty=True)
    _require_string_list(evidence or [], "evidence", allow_empty=True)
    _require_string_list(risks or [], "risks", allow_empty=True)
    _require_string_list(graph_delta or [], "graph_delta", allow_empty=True)
    _require_string_list(task_delta or [], "task_delta", allow_empty=True)
    _require_string_list(refactor_debt or [], "refactor_debt", allow_empty=True)
    normalized_tests = _normalize_tests(tests or [])

    checkpoint = {
        "schema_version": "2",
        "checkpoint_id": checkpoint_id,
        "parent_checkpoint_id": parent_checkpoint_id,
        "project_id": current["project_id"],
        "workstream_id": workstream_id,
        "objective_id": current["current_objective_id"],
        "agent_id": agent_id,
        "session_id": session_id,
        "observed_source_sha": current["observed_source_sha"],
        "event_watermark": current["event_watermark"],
        "projection_hash": current.get("projection_hash"),
        "context_pack_hash": None,
        "state_hash": hash_canonical(current),
        "authority_state": current["authority_state"],
        "completed": list(completed),
        "changed_paths": sorted(set(changed_paths or [])),
        "decisions": sorted(set(decisions or [])),
        "tests": normalized_tests,
        "evidence": sorted(set(evidence or [])),
        "blockers": list(blockers),
        "risks": list(risks or []),
        "graph_delta": list(graph_delta or []),
        "task_delta": list(task_delta or []),
        "refactor_debt": list(refactor_debt or []),
        "next_actions": list(next_actions),
        "resume_recipe": list(resume_recipe),
    }
    checkpoint["checkpoint_hash"] = hash_canonical(checkpoint)
    return checkpoint


def verify_checkpoint(checkpoint: dict[str, Any], *, state: dict[str, Any] | None = None) -> None:
    if type(checkpoint) is not dict:
        raise SurvivalContractError("checkpoint must be object")
    provided = checkpoint.get("checkpoint_hash")
    if not _is_hash(provided):
        raise SurvivalContractError("checkpoint_hash missing or malformed")
    state_hash = checkpoint.get("state_hash")
    if not _is_hash(state_hash):
        raise SurvivalContractError("state_hash missing or malformed")
    payload = dict(checkpoint)
    payload.pop("checkpoint_hash", None)
    if hash_canonical(payload) != provided:
        raise SurvivalContractError("checkpoint integrity mismatch")
    if state is not None:
        canonical = _normalize_state(state)
        if hash_canonical(canonical) != state_hash:
            raise SurvivalContractError("checkpoint state binding mismatch")
        if checkpoint.get("project_id") != canonical["project_id"]:
            raise SurvivalContractError("checkpoint project binding mismatch")
        if checkpoint.get("observed_source_sha") != canonical["observed_source_sha"]:
            raise SurvivalContractError("checkpoint source binding mismatch")
        if checkpoint.get("event_watermark") != canonical["event_watermark"]:
            raise SurvivalContractError("checkpoint watermark binding mismatch")


def evaluate_death_drill(
    state: dict[str, Any], report: dict[str, Any], *, elapsed_seconds: float,
    slo_seconds: float = DEFAULT_DEATH_DRILL_SLO_SECONDS,
) -> dict[str, Any]:
    if type(report) is not dict:
        raise SurvivalContractError("death-drill report must be object")
    if isinstance(elapsed_seconds, bool) or not isinstance(elapsed_seconds, (int, float)) or not math.isfinite(float(elapsed_seconds)) or elapsed_seconds < 0:
        raise SurvivalContractError("elapsed_seconds must be a finite non-negative number")
    if isinstance(slo_seconds, bool) or not isinstance(slo_seconds, (int, float)) or not math.isfinite(float(slo_seconds)) or slo_seconds <= 0:
        raise SurvivalContractError("slo_seconds must be a finite positive number")

    canonical = _normalize_state(state)
    required = {
        "project_id": canonical["project_id"],
        "current_objective_id": canonical["current_objective_id"],
        "observed_source_sha": canonical["observed_source_sha"],
        "event_watermark": canonical["event_watermark"],
        "active_workstreams": canonical["active_workstreams"],
        "active_claims": canonical["active_claims"],
        "blockers": canonical["blockers"],
        "verified_capabilities": canonical["verified_capabilities"],
        "unverified_capabilities": canonical["unverified_capabilities"],
        "next_safe_actions": canonical["next_safe_actions"],
    }
    mismatches: list[str] = []
    for field, expected in required.items():
        observed = report.get(field)
        if isinstance(expected, list):
            if type(observed) is not list or not _string_list(observed, allow_empty=True) or sorted(observed) != sorted(expected):
                mismatches.append(field)
        elif type(observed) is not type(expected) or observed != expected:
            mismatches.append(field)

    within_slo = float(elapsed_seconds) <= float(slo_seconds)
    passed = not mismatches and within_slo
    return {
        "passed": passed,
        "mismatches": mismatches,
        "score": (len(required) - len(mismatches)) / len(required),
        "within_slo": within_slo,
        "elapsed_seconds": float(elapsed_seconds),
        "slo_seconds": float(slo_seconds),
        "continuity_defect": bool(mismatches) or not within_slo,
        "state_hash": hash_canonical(canonical),
    }


def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    required = {"event_id", "sequence", "event_type", "project_id", "payload"}
    if type(event) is not dict or set(event) != required:
        raise SurvivalContractError("event must contain exactly event_id, sequence, event_type, project_id, payload")
    _require_text_value(event["event_id"], "event_id")
    if not _strict_nonnegative_int(event["sequence"]):
        raise SurvivalContractError("sequence must be non-negative integer")
    _require_text_value(event["event_type"], "event_type")
    _require_text_value(event["project_id"], "project_id")
    if type(event["payload"]) is not dict:
        raise SurvivalContractError("payload must be object")
    return dict(event)


def _normalize_state(state: dict[str, Any]) -> dict[str, Any]:
    if type(state) is not dict:
        raise SurvivalContractError("state must be object")
    watermark = state.get("event_watermark", 0)
    if not _strict_nonnegative_int(watermark):
        raise SurvivalContractError("invalid event watermark")
    current = {
        "schema_version": "2",
        "project_id": _state_text(state, "project_id"),
        "north_star": _state_text(state, "north_star"),
        "current_objective_id": _state_text(state, "current_objective_id"),
        "observed_source_sha": _state_text(state, "observed_source_sha"),
        "event_watermark": watermark,
        "authority_state": state.get("authority_state", "PROPOSED"),
        "active_workstreams": _normalized_string_set(state.get("active_workstreams", []), "active_workstreams"),
        "active_claims": _normalized_string_set(state.get("active_claims", []), "active_claims"),
        "blockers": _normalized_string_set(state.get("blockers", []), "blockers"),
        "verified_capabilities": _normalized_string_set(state.get("verified_capabilities", []), "verified_capabilities"),
        "unverified_capabilities": _normalized_string_set(state.get("unverified_capabilities", []), "unverified_capabilities"),
        "decisions": _normalized_string_set(state.get("decisions", []), "decisions"),
        "latest_checkpoint_id": state.get("latest_checkpoint_id"),
        "projection_hash": state.get("projection_hash"),
        "next_safe_actions": list(state.get("next_safe_actions", [])),
    }
    if current["authority_state"] not in AUTHORITY_STATES:
        raise SurvivalContractError("invalid authority state")
    if not _is_git_sha(current["observed_source_sha"]):
        raise SurvivalContractError("invalid observed source revision")
    if current["projection_hash"] is not None and not _is_hash(current["projection_hash"]):
        raise SurvivalContractError("invalid projection hash")
    if not _string_list(current["next_safe_actions"], allow_empty=True):
        raise SurvivalContractError("next_safe_actions must be string list")
    if current["latest_checkpoint_id"] is not None:
        _require_text_value(current["latest_checkpoint_id"], "latest_checkpoint_id")
    return current


def _apply(state: dict[str, Any], event: dict[str, Any]) -> None:
    kind, payload = event["event_type"], event["payload"]
    if kind == "objective.set":
        state["current_objective_id"] = _text(payload, "objective_id")
    elif kind == "source_revision.observed":
        sha = _text(payload, "observed_source_sha")
        if not _is_git_sha(sha):
            raise SurvivalContractError("invalid observed source revision event")
        state["observed_source_sha"] = sha
    elif kind == "authority.set":
        value = _text(payload, "authority_state")
        if value not in AUTHORITY_STATES:
            raise SurvivalContractError("invalid authority transition")
        state["authority_state"] = value
    elif kind == "workstream.started":
        _add(state, "active_workstreams", _text(payload, "workstream_id"))
    elif kind == "workstream.completed":
        _discard(state, "active_workstreams", _text(payload, "workstream_id"))
    elif kind == "claim.acquired":
        _add(state, "active_claims", _text(payload, "claim_id"))
    elif kind == "claim.released":
        _discard(state, "active_claims", _text(payload, "claim_id"))
    elif kind == "blocker.added":
        _add(state, "blockers", _text(payload, "blocker_id"))
    elif kind == "blocker.cleared":
        _discard(state, "blockers", _text(payload, "blocker_id"))
    elif kind == "capability.verified":
        capability = _text(payload, "capability_id")
        _discard(state, "unverified_capabilities", capability)
        _add(state, "verified_capabilities", capability)
    elif kind == "capability.unverified":
        capability = _text(payload, "capability_id")
        _discard(state, "verified_capabilities", capability)
        _add(state, "unverified_capabilities", capability)
    elif kind == "decision.accepted":
        _add(state, "decisions", _text(payload, "decision_id"))
    elif kind == "checkpoint.created":
        state["latest_checkpoint_id"] = _text(payload, "checkpoint_id")
    elif kind == "projection.updated":
        value = _text(payload, "projection_hash")
        if not _is_hash(value):
            raise SurvivalContractError("invalid projection hash event")
        state["projection_hash"] = value
    elif kind == "next_actions.set":
        actions = payload.get("next_safe_actions")
        if not _string_list(actions, allow_empty=False):
            raise SurvivalContractError("next_safe_actions must be non-empty string list")
        state["next_safe_actions"] = list(actions)
    else:
        raise SurvivalContractError(f"unsupported event_type {kind}")


def _normalize_tests(tests: Any) -> list[dict[str, Any]]:
    if type(tests) is not list:
        raise SurvivalContractError("tests must be list")
    normalized: list[dict[str, Any]] = []
    for item in tests:
        if type(item) is not dict:
            raise SurvivalContractError("test evidence must be object")
        required = {"test_id", "status", "source_sha"}
        optional = {"run_id", "evidence_hash"}
        if not required.issubset(item) or not set(item).issubset(required | optional):
            raise SurvivalContractError("test evidence fields invalid")
        _require_text_value(item["test_id"], "test_id")
        if item["status"] not in TEST_STATES:
            raise SurvivalContractError("invalid test status")
        if not _is_git_sha(item["source_sha"]):
            raise SurvivalContractError("invalid test source_sha")
        if item.get("run_id") is not None:
            _require_text_value(item["run_id"], "run_id")
        if item.get("evidence_hash") is not None and not _is_hash(item["evidence_hash"]):
            raise SurvivalContractError("invalid test evidence_hash")
        normalized.append(dict(item))
    return normalized


def _text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    _require_text_value(value, key)
    return value


def _state_text(state: dict[str, Any], key: str) -> str:
    value = state.get(key)
    _require_text_value(value, key)
    return value


def _require_text_value(value: Any, key: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise SurvivalContractError(f"{key} required")


def _require_string_list(value: Any, key: str, *, allow_empty: bool) -> None:
    if not _string_list(value, allow_empty=allow_empty):
        raise SurvivalContractError(f"{key} must be {'possibly-empty' if allow_empty else 'non-empty'} string list")


def _normalized_string_set(value: Any, key: str) -> list[str]:
    if not _string_list(value, allow_empty=True):
        raise SurvivalContractError(f"{key} must be string list")
    return sorted(set(value))


def _string_list(value: Any, *, allow_empty: bool) -> bool:
    return type(value) is list and (allow_empty or bool(value)) and all(
        isinstance(item, str) and bool(item) and len(item) <= 4096 for item in value
    )


def _strict_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _add(state: dict[str, Any], key: str, value: str) -> None:
    state[key] = sorted(set(state.get(key, [])) | {value})


def _discard(state: dict[str, Any], key: str, value: str) -> None:
    state[key] = sorted(set(state.get(key, [])) - {value})


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71 and all(
        c in "0123456789abcdef" for c in value[7:]
    )


def _is_git_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value)
