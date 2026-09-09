from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = "ggev2.realtime.v1"
FRESHNESS_RANK = {"FRESH": 0, "UNKNOWN": 1, "STALE": 2, "BLOCKED": 3}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def compile_realtime_state(
    *,
    project_state: Mapping[str, Any],
    source_revision: str,
    source_observations: Iterable[Mapping[str, Any]],
    governance: Mapping[str, Any],
    quality_gates: Mapping[str, Any],
    projection_revision: int = 1,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if len(source_revision) != 40 or any(ch not in "0123456789abcdef" for ch in source_revision):
        raise ValueError("source_revision must be lowercase 40-hex SHA")
    if projection_revision < 1:
        raise ValueError("projection_revision must be >= 1")

    observations = [_normalize_observation(item) for item in source_observations]
    observations.sort(key=lambda item: item["source_id"])
    freshness = _overall_freshness(observations)

    project_id = _required_text(project_state, "project_id")
    current_objective = _required_text(project_state, "current_objective_id")
    blockers = _sorted_unique(project_state.get("blockers", []))
    workstreams = _sorted_unique(project_state.get("active_workstreams", []))
    claims = _sorted_unique(project_state.get("active_claims", []))
    next_actions = [str(item) for item in project_state.get("next_safe_actions", [])]

    graph = _compile_graph(
        project_id=project_id,
        objective_id=current_objective,
        workstreams=workstreams,
        claims=claims,
        blockers=blockers,
        verified=_sorted_unique(project_state.get("verified_capabilities", [])),
        unverified=_sorted_unique(project_state.get("unverified_capabilities", [])),
    )

    drift = [
        {
            "source_id": item["source_id"],
            "status": item["status"],
            "revision": item["revision"],
        }
        for item in observations
        if item["status"] != "FRESH"
    ]

    semantic = {
        "schema_version": SCHEMA_VERSION,
        "source_revision": source_revision,
        "projection_revision": projection_revision,
        "freshness": freshness,
        "authority_state": str(project_state.get("authority_state", "UNKNOWN")),
        "event_watermark": int(project_state.get("event_watermark", 0)),
        "project": {
            "project_id": project_id,
            "north_star": _required_text(project_state, "north_star"),
            "current_objective_id": current_objective,
        },
        "source_observations": observations,
        "active_objectives": [current_objective],
        "active_workstreams": workstreams,
        "active_claims": claims,
        "blockers": blockers,
        "governance": deepcopy(dict(governance)),
        "quality_gates": deepcopy(dict(quality_gates)),
        "graph": graph,
        "drift": drift,
        "next_safe_actions": next_actions,
    }
    state_hash = sha256_json(semantic)
    return {
        **semantic,
        "generated_at": generated_at or utc_now(),
        "state_hash": state_hash,
    }


def _normalize_observation(raw: Mapping[str, Any]) -> dict[str, Any]:
    source_id = _required_text(raw, "source_id")
    status = str(raw.get("status", "UNKNOWN")).upper()
    if status not in FRESHNESS_RANK:
        raise ValueError(f"invalid source observation status: {status}")
    revision = raw.get("revision")
    if revision is not None and not isinstance(revision, str):
        raise ValueError("source observation revision must be string or null")
    refs = _sorted_unique(raw.get("evidence_refs", []))
    return {"source_id": source_id, "status": status, "revision": revision, "evidence_refs": refs}


def _overall_freshness(observations: list[dict[str, Any]]) -> str:
    if not observations:
        return "BLOCKED"
    return max((item["status"] for item in observations), key=lambda status: FRESHNESS_RANK[status])


def _compile_graph(*, project_id: str, objective_id: str, workstreams: list[str], claims: list[str], blockers: list[str], verified: list[str], unverified: list[str]) -> dict[str, Any]:
    nodes: list[dict[str, str]] = [
        {"id": project_id, "type": "Project"},
        {"id": objective_id, "type": "Objective"},
    ]
    edges: list[dict[str, str]] = [{"from": project_id, "to": objective_id, "type": "HAS_OBJECTIVE"}]

    for node_id in workstreams:
        nodes.append({"id": node_id, "type": "Workstream"})
        edges.append({"from": objective_id, "to": node_id, "type": "EXECUTED_BY_WORKSTREAM"})
    for node_id in claims:
        nodes.append({"id": node_id, "type": "Claim"})
        edges.append({"from": node_id, "to": objective_id, "type": "CLAIMS_SCOPE_OF"})
    for node_id in blockers:
        nodes.append({"id": node_id, "type": "Blocker"})
        edges.append({"from": node_id, "to": objective_id, "type": "BLOCKS"})
    for node_id in verified:
        nodes.append({"id": node_id, "type": "Capability"})
        edges.append({"from": node_id, "to": project_id, "type": "VERIFIED_FOR"})
    for node_id in unverified:
        nodes.append({"id": node_id, "type": "Capability"})
        edges.append({"from": node_id, "to": project_id, "type": "UNVERIFIED_FOR"})

    nodes = sorted({(item["id"], item["type"]): item for item in nodes}.values(), key=lambda item: (item["type"], item["id"]))
    edges = sorted(edges, key=lambda item: (item["type"], item["from"], item["to"]))
    return {"nodes": nodes, "edges": edges}


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be non-empty string")
    return value


def _sorted_unique(values: Any) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, (list, tuple, set)):
        raise ValueError("expected list-like string collection")
    result = []
    for item in values:
        if not isinstance(item, str) or not item:
            raise ValueError("collection items must be non-empty strings")
        result.append(item)
    return sorted(set(result))
