from __future__ import annotations

import copy
from typing import Any, Iterable

from .canonical_json import hash_canonical
from .survival import SurvivalContractError, reduce_events


class AcceptedEventStore:
    """In-memory SHADOW reference for accepted-event semantics.

    It is intentionally not a production database. Its purpose is to freeze append,
    deduplication, receipt, replay and recovery contracts before any durable backend is chosen.
    """

    def __init__(self, seed: dict[str, Any]):
        self._seed = reduce_events(copy.deepcopy(seed), [])
        self._state = copy.deepcopy(self._seed)
        self._events: list[dict[str, Any]] = []
        self._receipts: dict[str, str] = {}

    @property
    def state(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)

    @property
    def event_watermark(self) -> int:
        return int(self._state["event_watermark"])

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        if type(event) is not dict:
            raise SurvivalContractError("event must be object")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise SurvivalContractError("event_id required")
        semantic_hash = hash_canonical(event)
        existing = self._receipts.get(event_id)
        if existing is not None:
            if existing != semantic_hash:
                raise SurvivalContractError("same event identity with different semantic payload")
            return {
                "accepted": True,
                "duplicate": True,
                "event_id": event_id,
                "semantic_hash": semantic_hash,
                "event_watermark": self.event_watermark,
                "state_hash": hash_canonical(self._state),
            }

        next_state = reduce_events(self._state, [copy.deepcopy(event)])
        self._events.append(copy.deepcopy(event))
        self._receipts[event_id] = semantic_hash
        self._state = next_state
        return {
            "accepted": True,
            "duplicate": False,
            "event_id": event_id,
            "semantic_hash": semantic_hash,
            "event_watermark": self.event_watermark,
            "state_hash": hash_canonical(self._state),
        }

    def append_many(self, events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        receipts: list[dict[str, Any]] = []
        for event in events:
            receipts.append(self.append(event))
        return receipts

    def export_recovery_bundle(self) -> dict[str, Any]:
        bundle = {
            "schema_version": "1",
            "project_id": self._state["project_id"],
            "seed": copy.deepcopy(self._seed),
            "events": copy.deepcopy(self._events),
            "event_receipts": dict(sorted(self._receipts.items())),
            "event_watermark": self.event_watermark,
            "final_state_hash": hash_canonical(self._state),
        }
        bundle["bundle_hash"] = hash_canonical(bundle)
        return bundle


def recover_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    if type(bundle) is not dict:
        raise SurvivalContractError("recovery bundle must be object")
    provided_bundle_hash = bundle.get("bundle_hash")
    if not _is_hash(provided_bundle_hash):
        raise SurvivalContractError("bundle_hash missing or malformed")
    unsigned = copy.deepcopy(bundle)
    unsigned.pop("bundle_hash", None)
    if hash_canonical(unsigned) != provided_bundle_hash:
        raise SurvivalContractError("recovery bundle integrity mismatch")
    if bundle.get("schema_version") != "1":
        raise SurvivalContractError("unsupported recovery bundle schema")
    seed = bundle.get("seed")
    events = bundle.get("events")
    receipts = bundle.get("event_receipts")
    if type(events) is not list or type(receipts) is not dict:
        raise SurvivalContractError("recovery bundle events/receipts malformed")

    observed_receipts: dict[str, str] = {}
    for event in events:
        if type(event) is not dict:
            raise SurvivalContractError("recovery event must be object")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise SurvivalContractError("recovery event_id required")
        semantic_hash = hash_canonical(event)
        if event_id in observed_receipts and observed_receipts[event_id] != semantic_hash:
            raise SurvivalContractError("recovery bundle has conflicting duplicate event")
        observed_receipts[event_id] = semantic_hash
    if dict(sorted(observed_receipts.items())) != receipts:
        raise SurvivalContractError("event receipt set mismatch")

    recovered = reduce_events(seed, events)
    if recovered["project_id"] != bundle.get("project_id"):
        raise SurvivalContractError("recovery project mismatch")
    if recovered["event_watermark"] != bundle.get("event_watermark"):
        raise SurvivalContractError("recovery watermark mismatch")
    if hash_canonical(recovered) != bundle.get("final_state_hash"):
        raise SurvivalContractError("recovered state hash mismatch")
    return recovered


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71 and all(
        char in "0123456789abcdef" for char in value[7:]
    )
