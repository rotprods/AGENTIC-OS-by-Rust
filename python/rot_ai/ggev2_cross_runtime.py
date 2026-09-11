from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from rot_contracts.canonical_json import hash_canonical

from .ggev2_swarm import TelemetryEvent, compile_swarm


class CrossRuntimeIngestError(ValueError):
    pass


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise CrossRuntimeIngestError(f"invalid {field}")
    return value


def normalize_observation(runtime_id: str, raw: dict[str, Any]) -> tuple[TelemetryEvent, dict[str, Any]]:
    """Normalize one emitter record without granting authority.

    External bridges currently use ``authority=OBSERVATION_ONLY`` while the
    native emitter uses ``authority_class=OBSERVATION_ONLY``. Both are accepted
    only when they explicitly remain observation-only.
    """
    runtime_id = _require_text(runtime_id, "runtime_id")
    if not isinstance(raw, dict):
        raise CrossRuntimeIngestError("observation must be object")

    authority = raw.get("authority_class", raw.get("authority"))
    if authority != "OBSERVATION_ONLY":
        raise CrossRuntimeIngestError("observation must explicitly be OBSERVATION_ONLY")

    def tuple_of_text(name: str) -> tuple[str, ...]:
        value = raw.get(name, [])
        if value is None:
            return ()
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise CrossRuntimeIngestError(f"invalid {name}")
        return tuple(value)

    event = TelemetryEvent(
        event_type=_require_text(raw.get("event_type"), "event_type"),
        agent_id=_require_text(raw.get("agent_id"), "agent_id"),
        session_id=_require_text(raw.get("session_id"), "session_id"),
        project_id=_require_text(raw.get("project_id"), "project_id"),
        objective_id=_require_text(raw.get("objective_id"), "objective_id"),
        workstream_id=raw.get("workstream_id") if isinstance(raw.get("workstream_id"), str) and raw.get("workstream_id") else None,
        repo=_require_text(raw.get("repo"), "repo"),
        branch=_require_text(raw.get("branch"), "branch"),
        head_sha=_require_text(raw.get("head_sha"), "head_sha"),
        observed_at=_require_text(raw.get("observed_at"), "observed_at"),
        claim_id=raw.get("claim_id") if isinstance(raw.get("claim_id"), str) and raw.get("claim_id") else None,
        fencing_generation=raw.get("fencing_generation"),
        event_watermark=raw.get("event_watermark"),
        state_hash=raw.get("state_hash") if isinstance(raw.get("state_hash"), str) and raw.get("state_hash") else None,
        semantic_scopes=tuple_of_text("semantic_scopes"),
        resource_scopes=tuple_of_text("resource_scopes"),
        evidence_ids=tuple_of_text("evidence_ids"),
        next_action=raw.get("next_action") if isinstance(raw.get("next_action"), str) and raw.get("next_action") else None,
        freshness=raw.get("freshness", "UNKNOWN"),
    )
    record = event.as_record()
    envelope = {
        "runtime_id": runtime_id,
        "observation_hash": record["observation_hash"],
        "record": record,
        "authority_class": "DERIVED_OBSERVATION_ONLY",
    }
    envelope["envelope_hash"] = hash_canonical(envelope)
    return event, envelope


def compile_cross_runtime(
    batches: Iterable[dict[str, Any]],
    *,
    current_heads: dict[str, str],
) -> dict[str, Any]:
    """Compile deterministic multi-runtime visibility from observation batches.

    Exact duplicate envelopes are collapsed. If the same runtime/event identity
    arrives with conflicting content, the compile fails closed at the aggregate
    layer: conflicts remain visible and no swarm projection is produced.
    """
    normalized: list[tuple[TelemetryEvent, dict[str, Any]]] = []
    batch_count = 0
    for batch in batches:
        batch_count += 1
        if not isinstance(batch, dict):
            raise CrossRuntimeIngestError("batch must be object")
        runtime_id = _require_text(batch.get("runtime_id"), "runtime_id")
        observations = batch.get("observations")
        if not isinstance(observations, list):
            raise CrossRuntimeIngestError("observations must be array")
        for raw in observations:
            normalized.append(normalize_observation(runtime_id, raw))

    # Exact replay duplicates collapse deterministically.
    exact: dict[tuple[str, str], tuple[TelemetryEvent, dict[str, Any]]] = {}
    duplicate_count = 0
    for event, envelope in normalized:
        key = (envelope["runtime_id"], envelope["observation_hash"])
        if key in exact:
            duplicate_count += 1
            continue
        exact[key] = (event, envelope)

    unique = sorted(exact.values(), key=lambda item: (item[1]["runtime_id"], item[1]["observation_hash"]))

    # A runtime/event identity must be immutable under replay. We intentionally
    # do not pick a winner if two distinct observations claim the same identity.
    identities: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for _event, envelope in unique:
        record = envelope["record"]
        identity = (
            envelope["runtime_id"],
            record["agent_id"],
            record["session_id"],
            record["event_type"],
            record.get("event_watermark"),
            record.get("claim_id"),
        )
        identities[identity].append(envelope)

    conflicts: list[dict[str, Any]] = []
    for identity, members in sorted(identities.items(), key=lambda item: repr(item[0])):
        hashes = sorted({member["observation_hash"] for member in members})
        if len(hashes) > 1:
            conflicts.append({
                "identity": list(identity),
                "observation_hashes": hashes,
                "runtime_ids": sorted({member["runtime_id"] for member in members}),
                "classification": "CROSS_RUNTIME_OBSERVATION_CONFLICT",
                "authority_effect": "NONE",
            })

    runtimes = sorted({envelope["runtime_id"] for _, envelope in unique})
    if conflicts:
        swarm = None
        status = "COLLISION_BLOCKED"
    else:
        swarm = compile_swarm([event for event, _ in unique], current_heads=current_heads)
        status = "COMPILED"

    output = {
        "schema_version": "1",
        "authority_class": "DERIVED_OBSERVATION_ONLY",
        "status": status,
        "runtime_ids": runtimes,
        "batches_seen": batch_count,
        "observations_seen": len(normalized),
        "unique_observations": len(unique),
        "exact_duplicates_suppressed": duplicate_count,
        "conflicts": conflicts,
        "envelopes": [envelope for _, envelope in unique],
        "swarm": swarm,
        "promotion_authority": False,
        "accepted_event_authority": False,
    }
    output["cross_runtime_hash"] = hash_canonical(output)
    return output
