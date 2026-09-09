from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Iterable

from rot_contracts.canonical_json import hash_canonical

EVENT_TYPES = {"BOOT", "CLAIM", "HEARTBEAT", "EVIDENCE", "PREFLIGHT", "HANDOFF"}
FRESHNESS = {"FRESH", "STALE", "UNKNOWN", "BLOCKED"}


class SwarmTelemetryError(ValueError):
    pass


@dataclass(frozen=True)
class TelemetryEvent:
    event_type: str
    agent_id: str
    session_id: str
    project_id: str
    objective_id: str
    repo: str
    branch: str
    head_sha: str
    observed_at: str
    workstream_id: str | None = None
    claim_id: str | None = None
    fencing_generation: int | None = None
    event_watermark: int | None = None
    state_hash: str | None = None
    semantic_scopes: tuple[str, ...] = ()
    resource_scopes: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    next_action: str | None = None
    freshness: str = "UNKNOWN"

    def validate(self) -> None:
        if self.event_type not in EVENT_TYPES:
            raise SwarmTelemetryError("unsupported event_type")
        for field in ("agent_id", "session_id", "project_id", "objective_id", "repo", "branch", "head_sha", "observed_at"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value or len(value) > 1024:
                raise SwarmTelemetryError(f"invalid {field}")
        if len(self.head_sha) != 40 or any(ch not in "0123456789abcdef" for ch in self.head_sha):
            raise SwarmTelemetryError("invalid head_sha")
        if self.freshness not in FRESHNESS:
            raise SwarmTelemetryError("invalid freshness")
        if self.fencing_generation is not None and (not isinstance(self.fencing_generation, int) or isinstance(self.fencing_generation, bool) or self.fencing_generation < 0):
            raise SwarmTelemetryError("invalid fencing_generation")
        if self.event_watermark is not None and (not isinstance(self.event_watermark, int) or isinstance(self.event_watermark, bool) or self.event_watermark < 0):
            raise SwarmTelemetryError("invalid event_watermark")
        if self.event_type == "CLAIM" and (not self.claim_id or self.fencing_generation is None):
            raise SwarmTelemetryError("CLAIM requires claim_id and fencing_generation")
        if self.event_type == "HEARTBEAT" and self.event_watermark is None:
            raise SwarmTelemetryError("HEARTBEAT requires event_watermark")
        if self.event_type == "EVIDENCE" and not self.evidence_ids:
            raise SwarmTelemetryError("EVIDENCE requires evidence_ids")
        if self.event_type == "HANDOFF" and not self.next_action:
            raise SwarmTelemetryError("HANDOFF requires next_action")

    def as_record(self) -> dict[str, Any]:
        self.validate()
        record = {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "project_id": self.project_id,
            "objective_id": self.objective_id,
            "repo": self.repo,
            "branch": self.branch,
            "head_sha": self.head_sha,
            "observed_at": self.observed_at,
            "workstream_id": self.workstream_id,
            "claim_id": self.claim_id,
            "fencing_generation": self.fencing_generation,
            "event_watermark": self.event_watermark,
            "state_hash": self.state_hash,
            "semantic_scopes": sorted(set(self.semantic_scopes)),
            "resource_scopes": sorted(set(self.resource_scopes)),
            "evidence_ids": sorted(set(self.evidence_ids)),
            "next_action": self.next_action,
            "freshness": self.freshness,
            "authority_class": "OBSERVATION_ONLY",
        }
        record["observation_hash"] = hash_canonical(record)
        return record


def compile_swarm(events: Iterable[TelemetryEvent], *, current_heads: dict[str, str]) -> dict[str, Any]:
    records = [event.as_record() for event in events]
    sessions: dict[str, dict[str, Any]] = {}
    agents: dict[str, dict[str, Any]] = {}
    claims: dict[str, dict[str, Any]] = {}
    collisions: list[dict[str, Any]] = []
    stale_sessions: list[str] = []

    for record in sorted(records, key=lambda item: (item["session_id"], item["observed_at"], item["event_type"])):
        session = sessions.setdefault(record["session_id"], {
            "session_id": record["session_id"], "agent_id": record["agent_id"], "project_id": record["project_id"],
            "objective_id": record["objective_id"], "repo": record["repo"], "branch": record["branch"],
            "head_sha": record["head_sha"], "events": [], "latest_watermark": None, "latest_state_hash": None,
            "latest_observed_at": record["observed_at"], "freshness": record["freshness"], "next_action": None,
        })
        if session["agent_id"] != record["agent_id"] or session["project_id"] != record["project_id"]:
            raise SwarmTelemetryError("session identity collision")
        session["events"].append(record["event_type"])
        session["head_sha"] = record["head_sha"]
        session["latest_observed_at"] = record["observed_at"]
        session["freshness"] = record["freshness"]
        if record["event_watermark"] is not None:
            previous = session["latest_watermark"]
            if previous is not None and record["event_watermark"] < previous:
                raise SwarmTelemetryError("event watermark regression")
            session["latest_watermark"] = record["event_watermark"]
        if record["state_hash"] is not None:
            session["latest_state_hash"] = record["state_hash"]
        if record["next_action"] is not None:
            session["next_action"] = record["next_action"]
        agents.setdefault(record["agent_id"], {"agent_id": record["agent_id"], "sessions": []})
        if record["session_id"] not in agents[record["agent_id"]]["sessions"]:
            agents[record["agent_id"]]["sessions"].append(record["session_id"])
        if record["event_type"] == "CLAIM":
            claim_id = record["claim_id"]
            if claim_id in claims and claims[claim_id]["observation_hash"] != record["observation_hash"]:
                raise SwarmTelemetryError("claim identity collision")
            claims[claim_id] = copy.deepcopy(record)

    for session_id, session in sessions.items():
        current = current_heads.get(session["repo"])
        if current is None or current != session["head_sha"] or session["freshness"] in {"STALE", "BLOCKED"}:
            stale_sessions.append(session_id)

    claim_values = list(claims.values())
    for index, left in enumerate(claim_values):
        for right in claim_values[index + 1:]:
            if left["repo"] != right["repo"] or left["project_id"] != right["project_id"]:
                continue
            overlap = sorted(set(left["resource_scopes"]) & set(right["resource_scopes"]))
            semantic = sorted(set(left["semantic_scopes"]) & set(right["semantic_scopes"]))
            if overlap or semantic:
                collisions.append({
                    "left_claim_id": left["claim_id"], "right_claim_id": right["claim_id"],
                    "resource_overlap": overlap, "semantic_overlap": semantic,
                    "severity": "P1" if overlap else "P2",
                })

    graph = {"nodes": [], "edges": []}
    for agent in sorted(agents.values(), key=lambda item: item["agent_id"]):
        graph["nodes"].append({"id": agent["agent_id"], "type": "Agent"})
        for session_id in sorted(agent["sessions"]):
            graph["nodes"].append({"id": session_id, "type": "Session"})
            graph["edges"].append({"from": agent["agent_id"], "to": session_id, "type": "HAS_SESSION"})
    for claim in sorted(claims.values(), key=lambda item: item["claim_id"]):
        graph["nodes"].append({"id": claim["claim_id"], "type": "Claim"})
        graph["edges"].append({"from": claim["session_id"], "to": claim["claim_id"], "type": "CLAIMED_BY"})
    for collision in collisions:
        graph["edges"].append({"from": collision["left_claim_id"], "to": collision["right_claim_id"], "type": "COLLIDES_WITH", "severity": collision["severity"]})

    output = {
        "schema_version": "1",
        "authority_class": "DERIVED_OBSERVATION_ONLY",
        "agent_visibility": "PARTIAL" if not records else "OBSERVED_NOT_CANONICAL",
        "agents": sorted(agents.values(), key=lambda item: item["agent_id"]),
        "sessions": sorted(sessions.values(), key=lambda item: item["session_id"]),
        "claims": sorted(claims.values(), key=lambda item: item["claim_id"]),
        "collisions": collisions,
        "stale_sessions": sorted(stale_sessions),
        "graph": graph,
    }
    output["swarm_hash"] = hash_canonical(output)
    return output
