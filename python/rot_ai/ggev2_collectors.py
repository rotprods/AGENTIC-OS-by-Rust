from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Iterable


class CollectorError(ValueError):
    pass


@dataclass(frozen=True)
class ObservationEnvelope:
    source_id: str
    source_type: str
    observed_at: str
    source_revision: str | None
    freshness: str
    payload: dict[str, Any]
    authority: str = "OBSERVATION_ONLY"
    schema_version: str = "1"

    def as_dict(self) -> dict[str, Any]:
        data = {
            "schema_version": self.schema_version,
            "authority": self.authority,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "observed_at": self.observed_at,
            "source_revision": self.source_revision,
            "freshness": self.freshness,
            "payload": self.payload,
        }
        data["observation_hash"] = semantic_hash(data)
        return data


def semantic_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + sha256(raw).hexdigest()


def normalize_github_repo(raw: dict[str, Any], *, observed_at: str) -> ObservationEnvelope:
    repo = required_text(raw, "repository_full_name")
    default_branch = required_text(raw, "default_branch")
    payload = {
        "repository_full_name": repo,
        "default_branch": default_branch,
        "visibility": raw.get("visibility"),
        "archived": bool(raw.get("archived", False)),
        "permissions": dict(raw.get("permissions") or {}),
    }
    return ObservationEnvelope(
        source_id=f"github:repo:{repo}",
        source_type="github_repository",
        observed_at=observed_at,
        source_revision=None,
        freshness="OBSERVED",
        payload=payload,
    )


def normalize_github_branch(raw: dict[str, Any], *, repo: str, observed_at: str) -> ObservationEnvelope:
    branch = required_text(raw, "name")
    commit = raw.get("commit") or {}
    sha = required_text(commit, "sha")
    verification = ((commit.get("commit") or {}).get("verification") or {})
    protection = raw.get("protection") or {}
    payload = {
        "repository_full_name": repo,
        "branch": branch,
        "head_sha": sha,
        "protected": bool(raw.get("protected", False)),
        "required_status_enforcement": ((protection.get("required_status_checks") or {}).get("enforcement_level")),
        "commit_verified": bool(verification.get("verified", False)),
        "verification_reason": verification.get("reason"),
    }
    return ObservationEnvelope(
        source_id=f"github:branch:{repo}:{branch}",
        source_type="github_branch",
        observed_at=observed_at,
        source_revision=sha,
        freshness="OBSERVED",
        payload=payload,
    )


def normalize_projection(source_id: str, source_type: str, raw: dict[str, Any], *, observed_at: str) -> ObservationEnvelope:
    freshness = raw.get("freshness", "UNKNOWN")
    if freshness not in {"FRESH", "OBSERVED", "STALE", "BLOCKED", "UNKNOWN"}:
        raise CollectorError("invalid freshness")
    revision = raw.get("source_revision")
    if revision is not None and not isinstance(revision, str):
        raise CollectorError("source_revision must be string or null")
    return ObservationEnvelope(
        source_id=source_id,
        source_type=source_type,
        observed_at=observed_at,
        source_revision=revision,
        freshness=freshness,
        payload=dict(raw.get("payload") or {}),
    )


def compile_portfolio(observations: Iterable[ObservationEnvelope]) -> dict[str, Any]:
    envelopes = [item.as_dict() for item in observations]
    envelopes.sort(key=lambda item: item["source_id"])
    repos: dict[str, dict[str, Any]] = {}
    blockers: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for obs in envelopes:
        source_id = obs["source_id"]
        source_type = obs["source_type"]
        payload = obs["payload"]
        nodes[source_id] = {"id": source_id, "type": "SourceObservation", "freshness": obs["freshness"]}

        if source_type == "github_repository":
            repo = payload["repository_full_name"]
            repo_id = f"repo:{repo}"
            repos.setdefault(repo, {}).update(payload)
            nodes[repo_id] = {"id": repo_id, "type": "Repository", "name": repo}
            edges.append({"from": source_id, "type": "OBSERVES", "to": repo_id})

        if source_type == "github_branch":
            repo = payload["repository_full_name"]
            repo_id = f"repo:{repo}"
            branch_id = f"branch:{repo}:{payload['branch']}"
            repos.setdefault(repo, {}).update({
                "head_sha": payload["head_sha"],
                "branch": payload["branch"],
                "protected": payload["protected"],
                "commit_verified": payload["commit_verified"],
            })
            nodes[repo_id] = {"id": repo_id, "type": "Repository", "name": repo}
            nodes[branch_id] = {"id": branch_id, "type": "Branch", "head_sha": payload["head_sha"]}
            edges.extend([
                {"from": source_id, "type": "OBSERVES", "to": branch_id},
                {"from": branch_id, "type": "PART_OF", "to": repo_id},
            ])
            if not payload["protected"]:
                blockers.append({
                    "id": f"blocker:branch-protection:{repo}:{payload['branch']}",
                    "severity": "P1",
                    "category": "BRANCH_PROTECTION_MISSING",
                    "repository": repo,
                    "branch": payload["branch"],
                })

        if obs["freshness"] in {"STALE", "BLOCKED", "UNKNOWN"}:
            blockers.append({
                "id": f"blocker:source-freshness:{source_id}",
                "severity": "P1" if obs["freshness"] == "BLOCKED" else "P2",
                "category": "SOURCE_NOT_FRESH",
                "source_id": source_id,
                "freshness": obs["freshness"],
            })

    payload = {
        "schema_version": "1",
        "authority": "DERIVED_READ_ONLY",
        "repositories": {key: repos[key] for key in sorted(repos)},
        "observations": envelopes,
        "blockers": sorted(blockers, key=lambda item: item["id"]),
        "graph": {
            "nodes": [nodes[key] for key in sorted(nodes)],
            "edges": sorted(edges, key=lambda edge: (edge["from"], edge["type"], edge["to"])),
        },
    }
    payload["state_hash"] = semantic_hash(payload)
    return payload


def required_text(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise CollectorError(f"{key} must be a non-empty string")
    return value
