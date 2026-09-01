from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Iterable

from .canonical_json import hash_canonical
from .survival import FreshnessSeal, SurvivalContractError, assert_fresh


ACCESS_MODES = {"READ", "WRITE", "EXCLUSIVE_WRITE"}
RESOURCE_KINDS = {"file", "tree", "contract", "schema", "capability", "plan", "architecture"}
CLOCK_AUTHORITY = "EXTERNAL_LOGICAL_TICK_UNQUALIFIED"


@dataclass(frozen=True)
class ResourceAccess:
    resource: str
    mode: str

    def __post_init__(self) -> None:
        _parse_resource(self.resource)
        if self.mode not in ACCESS_MODES:
            raise SurvivalContractError("unsupported access mode")


class ClaimRegistry:
    """SHADOW reference registry for scope conflicts, leases and fencing.

    Logical time is supplied externally and is explicitly UNQUALIFIED for production authority.
    This reference implementation only enforces non-regression of observed logical ticks.
    Fencing generations are globally monotonic and never reset after release.
    """

    def __init__(self) -> None:
        self._claims: dict[str, dict[str, Any]] = {}
        self._generation = 0
        self._last_logical_tick = 0

    def _observe_tick(self, logical_tick: int) -> None:
        if not _strict_nonnegative_int(logical_tick):
            raise SurvivalContractError("logical_tick must be non-negative integer")
        if logical_tick < self._last_logical_tick:
            raise SurvivalContractError("logical clock regression")
        self._last_logical_tick = logical_tick

    def acquire(
        self, *, claim_id: str, agent_id: str, session_id: str, workstream_id: str,
        resources: Iterable[ResourceAccess], logical_tick: int, ttl_ticks: int,
        local_freshness: FreshnessSeal, live_freshness: FreshnessSeal,
    ) -> dict[str, Any]:
        assert_fresh(local_freshness, live_freshness)
        self._observe_tick(logical_tick)
        for field, value in (("claim_id", claim_id), ("agent_id", agent_id), ("session_id", session_id), ("workstream_id", workstream_id)):
            _require_text(value, field)
        if claim_id in self._claims:
            raise SurvivalContractError("claim identity reuse forbidden")
        if not isinstance(ttl_ticks, int) or isinstance(ttl_ticks, bool) or ttl_ticks <= 0:
            raise SurvivalContractError("ttl_ticks must be positive integer")
        normalized = sorted(list(resources), key=lambda item: (item.resource, item.mode))
        if not normalized:
            raise SurvivalContractError("claim requires at least one resource")
        if len({(item.resource, item.mode) for item in normalized}) != len(normalized):
            raise SurvivalContractError("duplicate resource access")

        conflicts: list[str] = []
        for existing in self._claims.values():
            if existing["status"] != "ACTIVE" or logical_tick > existing["lease_until"]:
                continue
            if _claims_conflict(normalized, [ResourceAccess(**item) for item in existing["resources"]]):
                conflicts.append(existing["claim_id"])
        if conflicts:
            raise SurvivalContractError("scope conflict with active claim(s): " + ",".join(sorted(conflicts)))

        self._generation += 1
        record = {
            "claim_id": claim_id,
            "agent_id": agent_id,
            "session_id": session_id,
            "workstream_id": workstream_id,
            "resources": [{"resource": item.resource, "mode": item.mode} for item in normalized],
            "acquired_at": logical_tick,
            "lease_until": logical_tick + ttl_ticks,
            "fencing_generation": self._generation,
            "clock_authority": CLOCK_AUTHORITY,
            "status": "ACTIVE",
            "freshness": {
                "observed_source_sha": live_freshness.observed_source_sha,
                "event_watermark": live_freshness.event_watermark,
                "projection_hash": live_freshness.projection_hash,
            },
        }
        record["claim_hash"] = hash_canonical(record)
        self._claims[claim_id] = record
        return copy.deepcopy(record)

    def release(self, claim_id: str, *, session_id: str) -> dict[str, Any]:
        record = self._claims.get(claim_id)
        if record is None:
            raise SurvivalContractError("unknown claim")
        if record["session_id"] != session_id:
            raise SurvivalContractError("claim release session mismatch")
        if record["status"] != "ACTIVE":
            raise SurvivalContractError("claim is not active")
        record = copy.deepcopy(record)
        record["status"] = "RELEASED"
        unsigned = dict(record)
        unsigned.pop("claim_hash", None)
        record["claim_hash"] = hash_canonical(unsigned)
        self._claims[claim_id] = record
        return copy.deepcopy(record)

    def validate_writer(self, claim_id: str, *, session_id: str, fencing_generation: int, logical_tick: int) -> None:
        self._observe_tick(logical_tick)
        record = self._claims.get(claim_id)
        if record is None:
            raise SurvivalContractError("unknown writer claim")
        if record["status"] != "ACTIVE":
            raise SurvivalContractError("writer claim not active")
        if record["session_id"] != session_id:
            raise SurvivalContractError("writer session mismatch")
        if not isinstance(fencing_generation, int) or isinstance(fencing_generation, bool):
            raise SurvivalContractError("invalid fencing generation")
        if fencing_generation != record["fencing_generation"]:
            raise SurvivalContractError("stale fencing generation")
        if logical_tick > record["lease_until"]:
            raise SurvivalContractError("writer lease expired")
        if not any(item["mode"] in {"WRITE", "EXCLUSIVE_WRITE"} for item in record["resources"]):
            raise SurvivalContractError("read-only claim cannot authorize writer")

    def snapshot(self, *, logical_tick: int) -> dict[str, Any]:
        self._observe_tick(logical_tick)
        claims = []
        for claim_id in sorted(self._claims):
            record = copy.deepcopy(self._claims[claim_id])
            effective_status = record["status"]
            if effective_status == "ACTIVE" and logical_tick > record["lease_until"]:
                effective_status = "EXPIRED"
            record["effective_status"] = effective_status
            claims.append(record)
        snapshot = {
            "schema_version": "1",
            "logical_tick": logical_tick,
            "clock_authority": CLOCK_AUTHORITY,
            "max_fencing_generation": self._generation,
            "claims": claims,
        }
        snapshot["snapshot_hash"] = hash_canonical(snapshot)
        return snapshot


def _claims_conflict(left: list[ResourceAccess], right: list[ResourceAccess]) -> bool:
    for a in left:
        for b in right:
            if not _resource_overlaps(a.resource, b.resource):
                continue
            if a.mode == "READ" and b.mode == "READ":
                continue
            return True
    return False


def _resource_overlaps(left: str, right: str) -> bool:
    left_kind, left_value = _parse_resource(left)
    right_kind, right_value = _parse_resource(right)
    if left_kind in {"file", "tree"} and right_kind in {"file", "tree"}:
        if left_kind == "file" and right_kind == "file":
            return left_value == right_value
        if left_kind == "tree" and right_kind == "tree":
            return _path_contains(left_value, right_value) or _path_contains(right_value, left_value)
        tree_value = left_value if left_kind == "tree" else right_value
        file_value = right_value if left_kind == "tree" else left_value
        return _path_contains(tree_value, file_value)
    return left_kind == right_kind and left_value == right_value


def _path_contains(tree: str, path: str) -> bool:
    tree = tree.rstrip("/")
    path = path.rstrip("/")
    return path == tree or path.startswith(tree + "/")


def _parse_resource(resource: str) -> tuple[str, str]:
    if not isinstance(resource, str) or ":" not in resource or len(resource) > 2048:
        raise SurvivalContractError("invalid resource scope")
    kind, value = resource.split(":", 1)
    if kind not in RESOURCE_KINDS or not value or value.startswith("/") or ".." in value.split("/"):
        raise SurvivalContractError("invalid resource scope")
    return kind, value


def _require_text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise SurvivalContractError(f"{field} required")


def _strict_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
