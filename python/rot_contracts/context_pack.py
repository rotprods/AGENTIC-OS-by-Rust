from __future__ import annotations

import copy
from typing import Any

from .canonical_json import canonicalize, hash_canonical
from .survival import FreshnessSeal, SurvivalContractError, assert_fresh, reduce_events
from .survival_graph import verify_projection


MAX_CONTEXT_CANONICAL_BYTES = 262_144


def compile_context_pack(
    state: dict[str, Any], *, projection: dict[str, Any], claim_snapshot: dict[str, Any],
    contracts_hash: str, session_id: str, workstream_id: str, relevant_context: dict[str, Any],
) -> dict[str, Any]:
    canonical = reduce_events(state, [])
    verify_projection(projection, canonical)
    _require_hash(contracts_hash, "contracts_hash")
    _require_text(session_id, "session_id")
    _require_text(workstream_id, "workstream_id")
    if type(relevant_context) is not dict:
        raise SurvivalContractError("relevant_context must be object")
    serialized_context = canonicalize(relevant_context).encode("utf-8")
    if len(serialized_context) > MAX_CONTEXT_CANONICAL_BYTES:
        raise SurvivalContractError("relevant_context exceeds bounded ContextPack budget")
    claim_hash = _claim_snapshot_hash(claim_snapshot)
    packet = {
        "schema_version": "1",
        "authority": "CACHE_ONLY",
        "context_trust": "UNTRUSTED_DATA",
        "project_id": canonical["project_id"],
        "session_id": session_id,
        "workstream_id": workstream_id,
        "source": {
            "observed_source_sha": canonical["observed_source_sha"],
            "event_watermark": canonical["event_watermark"],
            "state_hash": hash_canonical(canonical),
            "projection_hash": projection["projection_hash"],
            "claim_snapshot_hash": claim_hash,
            "contracts_hash": contracts_hash,
        },
        "context": copy.deepcopy(relevant_context),
        "invalidation": [
            "observed_source_sha_changed",
            "event_watermark_changed",
            "projection_hash_changed",
            "claim_snapshot_hash_changed",
            "contracts_hash_changed",
        ],
    }
    packet["context_pack_hash"] = hash_canonical(packet)
    return packet


def verify_context_pack(
    packet: dict[str, Any], *, live_state: dict[str, Any], live_projection: dict[str, Any],
    live_claim_snapshot: dict[str, Any], live_contracts_hash: str,
) -> None:
    if type(packet) is not dict:
        raise SurvivalContractError("ContextPack must be object")
    provided_hash = packet.get("context_pack_hash")
    _require_hash(provided_hash, "context_pack_hash")
    unsigned = copy.deepcopy(packet)
    unsigned.pop("context_pack_hash", None)
    if hash_canonical(unsigned) != provided_hash:
        raise SurvivalContractError("ContextPack integrity mismatch")
    if packet.get("authority") != "CACHE_ONLY":
        raise SurvivalContractError("ContextPack authority escalation")
    if packet.get("context_trust") != "UNTRUSTED_DATA":
        raise SurvivalContractError("ContextPack trust classification missing")
    context = packet.get("context")
    if type(context) is not dict or len(canonicalize(context).encode("utf-8")) > MAX_CONTEXT_CANONICAL_BYTES:
        raise SurvivalContractError("ContextPack context budget invalid")

    canonical = reduce_events(live_state, [])
    verify_projection(live_projection, canonical)
    source = packet.get("source")
    if type(source) is not dict:
        raise SurvivalContractError("ContextPack source binding missing")
    local = FreshnessSeal(
        source.get("observed_source_sha"),
        source.get("event_watermark"),
        source.get("projection_hash"),
    )
    live = FreshnessSeal(
        canonical["observed_source_sha"],
        canonical["event_watermark"],
        live_projection["projection_hash"],
    )
    assert_fresh(local, live)
    if source.get("state_hash") != hash_canonical(canonical):
        raise SurvivalContractError("stale ContextPack state hash")
    if source.get("claim_snapshot_hash") != _claim_snapshot_hash(live_claim_snapshot):
        raise SurvivalContractError("stale ContextPack claim snapshot")
    _require_hash(live_contracts_hash, "live_contracts_hash")
    if source.get("contracts_hash") != live_contracts_hash:
        raise SurvivalContractError("stale ContextPack contracts revision")


def _claim_snapshot_hash(snapshot: dict[str, Any]) -> str:
    if type(snapshot) is not dict:
        raise SurvivalContractError("claim snapshot must be object")
    provided = snapshot.get("snapshot_hash")
    _require_hash(provided, "claim snapshot_hash")
    unsigned = copy.deepcopy(snapshot)
    unsigned.pop("snapshot_hash", None)
    if hash_canonical(unsigned) != provided:
        raise SurvivalContractError("claim snapshot integrity mismatch")
    return provided


def _require_hash(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71 or any(
        char not in "0123456789abcdef" for char in value[7:]
    ):
        raise SurvivalContractError(f"{field} malformed")


def _require_text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise SurvivalContractError(f"{field} required")
