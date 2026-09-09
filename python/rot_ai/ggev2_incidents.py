from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from rot_contracts.canonical_json import hash_canonical


class IncidentCorrelationError(ValueError):
    pass


def correlate_signals(
    signals: Iterable[dict[str, Any]],
    *,
    current_heads: dict[str, str] | None = None,
    current_refs: dict[tuple[str, str], str] | None = None,
    current_ci: dict[tuple[str, ...], str] | None = None,
) -> dict[str, Any]:
    """Collapse untrusted provider signals into causal incident candidates.

    Ref-aware semantics are mandatory for suppression. A feature/PR-branch signal
    must never be compared to the repository default branch. Legacy repo-only
    ``current_heads`` is accepted only for signals explicitly scoped to ``main``
    or for legacy signals that carry no ref at all.
    """
    current_heads = current_heads or {}
    current_refs = current_refs or {}
    current_ci = current_ci or {}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unknown: list[dict[str, Any]] = []

    for raw in signals:
        signal = _normalize_signal(raw)
        if signal["repo"] is None or signal["sha"] is None:
            unknown.append({**signal, "classification": "UNKNOWN", "reason": "UNRESOLVED_REPO_OR_SHA"})
            continue
        fingerprint_material = {
            "repo": signal["repo"],
            "ref": signal["ref"],
            "workflow": signal["workflow"],
            "sha": signal["sha"],
            "failure_family": signal["failure_family"],
        }
        fingerprint = hash_canonical(fingerprint_material)
        groups[fingerprint].append(signal)

    incidents: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    for fingerprint, members in sorted(groups.items()):
        exemplar = members[0]
        repo = exemplar["repo"]
        ref = exemplar["ref"]
        sha = exemplar["sha"]
        workflow = exemplar["workflow"]

        current_ref_head = None
        if ref is not None:
            current_ref_head = current_refs.get((repo, ref))
            if current_ref_head is None and ref == "main":
                current_ref_head = current_heads.get(repo)
        else:
            # Backward compatibility only. New PR-run ingestion should resolve a
            # ref or remain UNKNOWN instead of comparing against default/main.
            current_ref_head = current_heads.get(repo)

        ci_state = _lookup_ci_state(current_ci, repo, ref, workflow)

        if ref is None and current_ref_head is None and ci_state == "UNKNOWN":
            incidents.append(
                _incident_record(
                    fingerprint, members, "UNKNOWN", "REF_UNRESOLVED", None, ci_state
                )
            )
            continue
        if ref is not None and current_ref_head is None and ci_state == "UNKNOWN":
            incidents.append(
                _incident_record(
                    fingerprint, members, "UNKNOWN", "CURRENT_REF_STATE_UNRESOLVED", None, ci_state
                )
            )
            continue
        if current_ref_head is not None and sha != current_ref_head and ci_state != "FAILURE":
            suppressed.append(
                _incident_record(
                    fingerprint,
                    members,
                    "SUPPRESSED",
                    "SUPERSEDED_REF_SHA",
                    current_ref_head,
                    ci_state,
                )
            )
            continue

        classification = "ACTIVE" if ci_state == "FAILURE" or sha == current_ref_head else "UNKNOWN"
        if ci_state == "FAILURE":
            reason = "CURRENT_FAILURE_CONFIRMED"
        elif sha == current_ref_head:
            reason = "CURRENT_REF_SHA_SIGNAL"
        else:
            reason = "CURRENT_STATE_UNRESOLVED"
        incidents.append(
            _incident_record(fingerprint, members, classification, reason, current_ref_head, ci_state)
        )

    output = {
        "schema_version": "2",
        "authority_class": "DERIVED_SIGNAL_ONLY",
        "incident_identity": ["repo", "ref", "workflow", "sha", "failure_family"],
        "incidents": incidents,
        "suppressed": suppressed,
        "unknown": sorted(
            unknown, key=lambda item: (item.get("source") or "", item.get("signal_id") or "")
        ),
        "metrics": {
            "signals_seen": sum(len(values) for values in groups.values()) + len(unknown),
            "causal_groups": len(groups),
            "active": sum(1 for item in incidents if item["classification"] == "ACTIVE"),
            "unknown": sum(1 for item in incidents if item["classification"] == "UNKNOWN") + len(unknown),
            "suppressed": len(suppressed),
        },
    }
    output["incident_graph_hash"] = hash_canonical(output)
    return output


def _lookup_ci_state(
    current_ci: dict[tuple[str, ...], str], repo: str, ref: str | None, workflow: str | None
) -> str:
    workflow_key = workflow or ""
    if ref is not None:
        value = current_ci.get((repo, ref, workflow_key))
        if value is not None:
            return value
    # Compatibility fallback for legacy callers only.
    return current_ci.get((repo, workflow_key), "UNKNOWN")


def _normalize_signal(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise IncidentCorrelationError("signal must be object")
    signal_id = raw.get("signal_id")
    source = raw.get("source")
    if not isinstance(signal_id, str) or not signal_id or not isinstance(source, str) or not source:
        raise IncidentCorrelationError("signal_id and source required")
    repo = raw.get("repo") if isinstance(raw.get("repo"), str) and raw.get("repo") else None
    sha = raw.get("sha") if isinstance(raw.get("sha"), str) and len(raw.get("sha")) == 40 else None
    if sha is not None and any(ch not in "0123456789abcdef" for ch in sha):
        sha = None
    ref = raw.get("ref") if isinstance(raw.get("ref"), str) and raw.get("ref") else None
    workflow = raw.get("workflow") if isinstance(raw.get("workflow"), str) and raw.get("workflow") else None
    failure_family = (
        raw.get("failure_family")
        if isinstance(raw.get("failure_family"), str) and raw.get("failure_family")
        else "UNKNOWN_FAILURE"
    )
    observed_at = raw.get("observed_at") if isinstance(raw.get("observed_at"), str) else None
    return {
        "signal_id": signal_id,
        "source": source,
        "repo": repo,
        "ref": ref,
        "sha": sha,
        "workflow": workflow,
        "failure_family": failure_family,
        "observed_at": observed_at,
        "authority_class": "UNTRUSTED_SIGNAL_INPUT",
    }


def _incident_record(
    fingerprint: str,
    members: list[dict[str, Any]],
    classification: str,
    reason: str,
    current_ref_head: str | None,
    ci_state: str,
) -> dict[str, Any]:
    exemplar = members[0]
    return {
        "incident_id": f"incident:{fingerprint}",
        "causal_fingerprint": fingerprint,
        "classification": classification,
        "reason": reason,
        "repo": exemplar["repo"],
        "ref": exemplar["ref"],
        "workflow": exemplar["workflow"],
        "sha": exemplar["sha"],
        "failure_family": exemplar["failure_family"],
        "signal_count": len(members),
        "signal_ids": sorted(item["signal_id"] for item in members),
        "sources": sorted({item["source"] for item in members}),
        "current_ref_head": current_ref_head,
        "current_ci_state": ci_state,
        "authority_class": "DERIVED_SIGNAL_ONLY",
    }
