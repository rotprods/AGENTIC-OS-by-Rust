from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .canonical_json import hash_canonical


AUTHORITY_STATES = {
    "PROPOSED", "IMPLEMENTED", "EXECUTED", "VERIFIED",
    "EMPIRICALLY_QUALIFIED", "BLOCKED", "DEGRADED_EXTERNAL", "SUPERSEDED",
}


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
    if local.projection_hash is not None and live.projection_hash is not None and local.projection_hash != live.projection_hash:
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
        if event["sequence"] <= previous_sequence:
            raise SurvivalContractError("event sequence must advance seed watermark strictly")
        previous_sequence = event["sequence"]
        seen[event_id] = event_hash
        if event["project_id"] != state["project_id"]:
            raise SurvivalContractError("cross-project event rejected")
        _apply(state, event)
        state["event_watermark"] = event["sequence"]
    return _normalize_state(state)


def build_checkpoint(state: dict[str, Any], *, checkpoint_id: str, agent_id: str, session_id: str,
                     workstream_id: str, completed: list[str], blockers: list[str], next_actions: list[str],
                     resume_recipe: list[str], parent_checkpoint_id: str | None = None,
                     tests: list[dict[str, Any]] | None = None, evidence: list[str] | None = None,
                     changed_paths: list[str] | None = None, decisions: list[str] | None = None,
                     risks: list[str] | None = None, graph_delta: list[str] | None = None,
                     task_delta: list[str] | None = None, refactor_debt: list[str] | None = None) -> dict[str, Any]:
    current = _normalize_state(state)
    for field, value in (("checkpoint_id", checkpoint_id), ("agent_id", agent_id), ("session_id", session_id), ("workstream_id", workstream_id)):
        _require_text_value(value, field)
    if not _string_list(next_actions, allow_empty=False) or not _string_list(resume_recipe, allow_empty=False):
        raise SurvivalContractError("checkpoint requires non-empty next_actions and resume_recipe")
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
        "authority_state": current["authority_state"],
        "completed": list(completed),
        "changed_paths": sorted(set(changed_paths or [])),
        "decisions": sorted(set(decisions or [])),
        "tests": list(tests or []),
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


def verify_checkpoint(checkpoint: dict[str, Any]) -> None:
    provided = checkpoint.get("checkpoint_hash")
    if not _is_hash(provided):
        raise SurvivalContractError("checkpoint_hash missing or malformed")
    payload = dict(checkpoint)
    payload.pop("checkpoint_hash", None)
    if hash_canonical(payload) != provided:
        raise SurvivalContractError("checkpoint integrity mismatch")


def evaluate_death_drill(state: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    if type(report) is not dict:
        raise SurvivalContractError("death-drill report must be object")
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
    return {
        "passed": not mismatches,
        "mismatches": mismatches,
        "score": (len(required) - len(mismatches)) / len(required),
        "continuity_defect": bool(mismatches),
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


def _normalized_string_set(value: Any, key: str) -> list[str]:
    if not _string_list(value, allow_empty=True):
        raise SurvivalContractError(f"{key} must be string list")
    return sorted(set(value))


def _string_list(value: Any, *, allow_empty: bool) -> bool:
    return type(value) is list and (allow_empty or bool(value)) and all(isinstance(item, str) and bool(item) and len(item) <= 4096 for item in value)


def _strict_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _add(state: dict[str, Any], key: str, value: str) -> None:
    state[key] = sorted(set(state.get(key, [])) | {value})


def _discard(state: dict[str, Any], key: str, value: str) -> None:
    state[key] = sorted(set(state.get(key, [])) - {value})


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71 and all(c in "0123456789abcdef" for c in value[7:])


def _is_git_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value)
