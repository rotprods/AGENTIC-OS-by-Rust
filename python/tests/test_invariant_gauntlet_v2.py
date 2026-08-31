from __future__ import annotations

import copy
import random
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.survival import FreshnessSeal, SurvivalContractError
from rot_contracts.survival_store import AcceptedEventStore, recover_from_bundle


HEAD = "a" * 40
PROJECT = "rot://project/agentic-os"
SEED = 0xA613


def seed_state() -> dict:
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/invariant-gauntlet",
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
        "next_safe_actions": ["execute deterministic invariant corpus"],
    }


def event(sequence: int, event_type: str, payload: dict) -> dict:
    return {
        "event_id": f"rot://event/invariant/{sequence:04d}",
        "sequence": sequence,
        "event_type": event_type,
        "project_id": PROJECT,
        "payload": payload,
    }


def deterministic_stream(blocks: int = 4) -> list[dict]:
    specs: list[tuple[str, dict]] = []
    for block in range(blocks):
        blocker = f"rot://blocker/{block}"
        workstream = f"rot://workstream/{block}"
        claim = f"rot://claim/{block}"
        capability = f"rot://capability/{block}"
        specs.extend(
            [
                ("blocker.added", {"blocker_id": blocker}),
                ("blocker.cleared", {"blocker_id": blocker}),
                ("workstream.started", {"workstream_id": workstream}),
                ("workstream.completed", {"workstream_id": workstream}),
                ("claim.acquired", {"claim_id": claim}),
                ("claim.released", {"claim_id": claim}),
                ("capability.unverified", {"capability_id": capability}),
                ("capability.verified", {"capability_id": capability}),
                ("decision.accepted", {"decision_id": f"rot://decision/{block}"}),
                ("checkpoint.created", {"checkpoint_id": f"rot://checkpoint/property/{block}"}),
                ("projection.updated", {"projection_hash": "sha256:" + format(block + 1, "x") * 64}),
                ("next_actions.set", {"next_safe_actions": [f"next-{block}", f"verify-{block}"]}),
                ("objective.set", {"objective_id": f"rot://objective/property/{block}"}),
                ("source_revision.observed", {"observed_source_sha": format(block + 1, "x") * 40}),
                ("authority.set", {"authority_state": "IMPLEMENTED"}),
            ]
        )
    return [event(index, kind, payload) for index, (kind, payload) in enumerate(specs, start=1)]


def reseal(bundle: dict) -> dict:
    result = copy.deepcopy(bundle)
    result.pop("bundle_hash", None)
    result["bundle_hash"] = hash_canonical(result)
    return result


class DeterministicInvariantGauntletV2(unittest.TestCase):
    def test_every_prefix_recovery_matches_live_state(self) -> None:
        store = AcceptedEventStore(seed_state())
        for index, current in enumerate(deterministic_stream(), start=1):
            store.append(current)
            if index % 3 == 0 or index == len(deterministic_stream()):
                bundle = store.export_recovery_bundle()
                recovered = recover_from_bundle(bundle)
                self.assertEqual(recovered, store.state)
                self.assertEqual(hash_canonical(recovered), bundle["final_state_hash"])
                self.assertEqual(recovered["event_watermark"], index)

    def test_event_transport_order_is_not_semantic_order(self) -> None:
        store = AcceptedEventStore(seed_state())
        store.append_many(deterministic_stream())
        expected = store.state
        bundle = store.export_recovery_bundle()
        shuffled = copy.deepcopy(bundle)
        random.Random(SEED).shuffle(shuffled["events"])
        shuffled = reseal(shuffled)
        self.assertEqual(recover_from_bundle(shuffled), expected)

    def test_exact_duplicate_events_are_idempotent_during_recovery(self) -> None:
        store = AcceptedEventStore(seed_state())
        store.append_many(deterministic_stream(2))
        bundle = store.export_recovery_bundle()
        duplicated = copy.deepcopy(bundle)
        rng = random.Random(SEED)
        for index in sorted(rng.sample(range(len(duplicated["events"])), 8), reverse=True):
            duplicated["events"].insert(index, copy.deepcopy(duplicated["events"][index]))
        duplicated = reseal(duplicated)
        self.assertEqual(recover_from_bundle(duplicated), store.state)

    def test_resealed_sequence_mutations_never_bypass_event_horizon(self) -> None:
        store = AcceptedEventStore(seed_state())
        store.append_many(deterministic_stream(2))
        original = store.export_recovery_bundle()
        rng = random.Random(SEED)
        for index in rng.sample(range(len(original["events"])), 10):
            with self.subTest(index=index):
                mutated = copy.deepcopy(original)
                target = mutated["events"][index]
                target["sequence"] += 1000 + index
                mutated["event_receipts"][target["event_id"]] = hash_canonical(target)
                mutated = reseal(mutated)
                with self.assertRaisesRegex(SurvivalContractError, "sequence discontinuity"):
                    recover_from_bundle(mutated)

    def test_resealed_duplicate_identity_conflicts_fail_closed(self) -> None:
        store = AcceptedEventStore(seed_state())
        store.append_many(deterministic_stream(2))
        original = store.export_recovery_bundle()
        rng = random.Random(SEED)
        pairs = [rng.sample(range(len(original["events"])), 2) for _ in range(8)]
        for source_index, target_index in pairs:
            with self.subTest(source=source_index, target=target_index):
                mutated = copy.deepcopy(original)
                source = mutated["events"][source_index]
                target = mutated["events"][target_index]
                target["event_id"] = source["event_id"]
                mutated = reseal(mutated)
                with self.assertRaisesRegex(SurvivalContractError, "conflicting duplicate event"):
                    recover_from_bundle(mutated)

    def test_rejected_appends_do_not_mutate_state_or_receipts(self) -> None:
        base = deterministic_stream(1)
        rng = random.Random(SEED)
        for mutation_index in rng.sample(range(len(base)), 8):
            with self.subTest(mutation_index=mutation_index):
                store = AcceptedEventStore(seed_state())
                before = store.export_recovery_bundle()
                bad = copy.deepcopy(base[mutation_index])
                bad["sequence"] += 500
                with self.assertRaises(SurvivalContractError):
                    store.append(bad)
                after = store.export_recovery_bundle()
                self.assertEqual(before, after)

    def test_fencing_generations_are_monotonic_and_released_writers_never_revive(self) -> None:
        seal = FreshnessSeal(HEAD, 0, None)
        registry = ClaimRegistry()
        generations: list[int] = []
        released: list[tuple[str, str, int]] = []
        for tick in range(1, 65):
            claim_id = f"claim-{tick}"
            session_id = f"session-{tick}"
            record = registry.acquire(
                claim_id=claim_id,
                agent_id=f"agent-{tick}",
                session_id=session_id,
                workstream_id=f"workstream-{tick}",
                resources=[ResourceAccess("contract:survival", "WRITE")],
                logical_tick=tick,
                ttl_ticks=128,
                local_freshness=seal,
                live_freshness=seal,
            )
            generations.append(record["fencing_generation"])
            registry.release(claim_id, session_id=session_id)
            released.append((claim_id, session_id, record["fencing_generation"]))
        self.assertEqual(generations, list(range(1, 65)))
        for claim_id, session_id, generation in released:
            with self.subTest(claim_id=claim_id):
                with self.assertRaisesRegex(SurvivalContractError, "not active"):
                    registry.validate_writer(
                        claim_id,
                        session_id=session_id,
                        fencing_generation=generation,
                        logical_tick=64,
                    )

    def test_expired_writer_takeovers_never_reuse_generation(self) -> None:
        seal = FreshnessSeal(HEAD, 0, None)
        registry = ClaimRegistry()
        previous_generation = 0
        prior_claims: list[tuple[str, str, int, int]] = []
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
            self.assertGreater(record["fencing_generation"], previous_generation)
            previous_generation = record["fencing_generation"]
            prior_claims.append((claim_id, session_id, record["fencing_generation"], tick + 2))
        self.assertEqual(previous_generation, 24)
        for claim_id, session_id, generation, expired_tick in prior_claims[:-1]:
            with self.subTest(claim_id=claim_id):
                with self.assertRaises(SurvivalContractError):
                    registry.validate_writer(
                        claim_id,
                        session_id=session_id,
                        fencing_generation=generation,
                        logical_tick=max(expired_tick, 70),
                    )


if __name__ == "__main__":
    unittest.main()
