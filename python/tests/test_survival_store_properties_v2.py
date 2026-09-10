from __future__ import annotations

import copy
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.survival import FreshnessSeal, SurvivalContractError
from rot_contracts.survival_store import AcceptedEventStore, recover_from_bundle


HEAD = "a" * 40
PROJECT = "rot://project/agentic-os"


def seed_state() -> dict:
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/store-property-union",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": [],
        "unverified_capabilities": [],
        "decisions": [],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["execute durable-store property union"],
    }


def event(sequence: int, event_type: str, payload: dict) -> dict:
    return {
        "event_id": f"rot://event/store-property/{sequence:04d}",
        "sequence": sequence,
        "event_type": event_type,
        "project_id": PROJECT,
        "payload": payload,
    }


def deterministic_stream(blocks: int = 3) -> list[dict]:
    specs: list[tuple[str, dict]] = []
    for block in range(blocks):
        blocker = f"rot://blocker/store-property/{block}"
        workstream = f"rot://workstream/store-property/{block}"
        capability = f"rot://capability/store-property/{block}"
        specs.extend(
            [
                ("blocker.added", {"blocker_id": blocker}),
                ("blocker.cleared", {"blocker_id": blocker}),
                ("workstream.started", {"workstream_id": workstream}),
                ("workstream.completed", {"workstream_id": workstream}),
                ("capability.unverified", {"capability_id": capability}),
                ("capability.verified", {"capability_id": capability}),
                ("decision.accepted", {"decision_id": f"rot://decision/store-property/{block}"}),
                ("next_actions.set", {"next_safe_actions": [f"next-{block}", f"verify-{block}"]}),
            ]
        )
    return [event(index, kind, payload) for index, (kind, payload) in enumerate(specs, start=1)]


def reseal(bundle: dict) -> dict:
    result = copy.deepcopy(bundle)
    result.pop("bundle_hash", None)
    result["bundle_hash"] = hash_canonical(result)
    return result


class SurvivalStorePropertyUnionV2Tests(unittest.TestCase):
    def test_every_durable_prefix_recovers_exact_live_store_state(self) -> None:
        store = AcceptedEventStore(seed_state())
        for index, current in enumerate(deterministic_stream(), start=1):
            store.append(current)
            bundle = store.export_recovery_bundle()
            recovered = recover_from_bundle(bundle)
            self.assertEqual(recovered, store.state)
            self.assertEqual(hash_canonical(recovered), bundle["final_state_hash"])
            self.assertEqual(recovered["event_watermark"], index)

    def test_exact_duplicate_events_in_recovery_bundle_are_idempotent(self) -> None:
        store = AcceptedEventStore(seed_state())
        store.append_many(deterministic_stream(2))
        bundle = store.export_recovery_bundle()
        duplicated = copy.deepcopy(bundle)
        for index in (1, 4, 7, 10, 13):
            duplicated["events"].insert(index, copy.deepcopy(duplicated["events"][index]))
        duplicated = reseal(duplicated)
        self.assertEqual(recover_from_bundle(duplicated), store.state)

    def test_rejected_append_is_atomic_for_state_receipts_and_bundle(self) -> None:
        stream = deterministic_stream(1)
        for mutation_index, candidate in enumerate(stream):
            with self.subTest(mutation_index=mutation_index):
                store = AcceptedEventStore(seed_state())
                before = store.export_recovery_bundle()
                bad = copy.deepcopy(candidate)
                bad["sequence"] += 500 + mutation_index
                with self.assertRaises(SurvivalContractError):
                    store.append(bad)
                after = store.export_recovery_bundle()
                self.assertEqual(before, after)

    def test_expiry_takeovers_never_reuse_fencing_generation(self) -> None:
        seal = FreshnessSeal(HEAD, 0, None)
        registry = ClaimRegistry()
        generations: list[int] = []
        prior_claims: list[tuple[str, str, int]] = []
        for index in range(24):
            tick = index * 3
            claim_id = f"takeover-{index}"
            session_id = f"takeover-session-{index}"
            record = registry.acquire(
                claim_id=claim_id,
                agent_id=f"takeover-agent-{index}",
                session_id=session_id,
                workstream_id=f"takeover-workstream-{index}",
                resources=[ResourceAccess("file:STATE.md", "EXCLUSIVE_WRITE")],
                logical_tick=tick,
                ttl_ticks=1,
                local_freshness=seal,
                live_freshness=seal,
            )
            generation = record["fencing_generation"]
            generations.append(generation)
            prior_claims.append((claim_id, session_id, generation))
        self.assertEqual(generations, list(range(1, 25)))
        for claim_id, session_id, generation in prior_claims[:-1]:
            with self.subTest(claim_id=claim_id):
                with self.assertRaises(SurvivalContractError):
                    registry.validate_writer(
                        claim_id,
                        session_id=session_id,
                        fencing_generation=generation,
                        logical_tick=72,
                    )


if __name__ == "__main__":
    unittest.main()
