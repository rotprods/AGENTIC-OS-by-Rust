from __future__ import annotations

import copy
import random
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.survival import (
    FreshnessSeal,
    SurvivalContractError,
    assert_fresh,
    build_checkpoint,
    reduce_events,
    verify_checkpoint,
)


SEED = 0xC0520D
HEAD = "a" * 40
HEAD2 = "b" * 40
PROJECT = "rot://project/agentic-os"
PROJECTION = "sha256:" + "1" * 64


def seed_state() -> dict:
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/property-assurance",
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
        "next_safe_actions": ["continue-property-assurance"],
    }


def event(sequence: int, event_id: str, event_type: str, payload: dict) -> dict:
    return {
        "event_id": event_id,
        "sequence": sequence,
        "event_type": event_type,
        "project_id": PROJECT,
        "payload": payload,
    }


def event_chain(count: int = 32) -> list[dict]:
    result = []
    for sequence in range(1, count + 1):
        if sequence % 4 == 1:
            result.append(event(sequence, f"e{sequence}", "blocker.added", {"blocker_id": f"b{sequence}"}))
        elif sequence % 4 == 2:
            result.append(event(sequence, f"e{sequence}", "decision.accepted", {"decision_id": f"d{sequence}"}))
        elif sequence % 4 == 3:
            result.append(event(sequence, f"e{sequence}", "workstream.started", {"workstream_id": f"w{sequence}"}))
        else:
            result.append(event(sequence, f"e{sequence}", "next_actions.set", {"next_safe_actions": [f"n{sequence}"]}))
    return result


class SurvivalDeterministicPropertyTests(unittest.TestCase):
    def test_replay_is_invariant_across_seeded_input_permutations(self) -> None:
        rng = random.Random(SEED)
        canonical_events = event_chain()
        oracle = reduce_events(seed_state(), canonical_events)
        oracle_hash = hash_canonical(oracle)
        for case in range(64):
            candidate = copy.deepcopy(canonical_events)
            rng.shuffle(candidate)
            with self.subTest(case=case):
                observed = reduce_events(seed_state(), candidate)
                self.assertEqual(observed, oracle)
                self.assertEqual(hash_canonical(observed), oracle_hash)

    def test_any_internal_sequence_gap_fails_closed(self) -> None:
        canonical_events = event_chain(24)
        # Removing the terminal event yields a valid shorter prefix. Internal holes,
        # however, must always be rejected by the reducer itself.
        for removed_index in range(len(canonical_events) - 1):
            candidate = canonical_events[:removed_index] + canonical_events[removed_index + 1 :]
            with self.subTest(removed_sequence=removed_index + 1):
                with self.assertRaisesRegex(SurvivalContractError, "discontinuity"):
                    reduce_events(seed_state(), candidate)

    def test_terminal_truncation_requires_external_watermark_to_detect(self) -> None:
        canonical_events = event_chain(24)
        truncated = reduce_events(seed_state(), canonical_events[:-1])
        complete = reduce_events(seed_state(), canonical_events)
        self.assertEqual(truncated["event_watermark"], 23)
        self.assertEqual(complete["event_watermark"], 24)
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            assert_fresh(
                FreshnessSeal(HEAD, truncated["event_watermark"], None),
                FreshnessSeal(HEAD, complete["event_watermark"], None),
            )

    def test_duplicate_identity_with_mutated_payload_never_replays(self) -> None:
        rng = random.Random(SEED)
        for case in range(40):
            blocker_a = f"a-{rng.getrandbits(64):016x}"
            blocker_b = f"b-{rng.getrandbits(64):016x}"
            events = [
                event(1, "same-id", "blocker.added", {"blocker_id": blocker_a}),
                event(2, "same-id", "blocker.added", {"blocker_id": blocker_b}),
            ]
            with self.subTest(case=case):
                with self.assertRaisesRegex(SurvivalContractError, "same event identity"):
                    reduce_events(seed_state(), events)

    def test_checkpoint_single_field_tampering_is_always_detected(self) -> None:
        state = seed_state()
        checkpoint = build_checkpoint(
            state,
            checkpoint_id="rot://checkpoint/agentic-os/property",
            agent_id="rot://agent/test/property",
            session_id="rot://session/test/property/unique",
            workstream_id="rot://workstream/property",
            completed=["baseline"],
            blockers=["external"],
            next_actions=["next"],
            resume_recipe=["reconstruct", "verify"],
            decisions=["decision-a"],
            evidence=["evidence-a"],
            risks=["risk-a"],
        )
        verify_checkpoint(checkpoint, state=state)
        mutations = {
            "completed": lambda value: value + ["forged"],
            "blockers": lambda value: value + ["forged"],
            "next_actions": lambda value: value + ["forged"],
            "resume_recipe": lambda value: value + ["forged"],
            "decisions": lambda value: value + ["forged"],
            "evidence": lambda value: value + ["forged"],
            "risks": lambda value: value + ["forged"],
            "event_watermark": lambda value: value + 1,
        }
        for field, mutate in mutations.items():
            tampered = copy.deepcopy(checkpoint)
            tampered[field] = mutate(tampered[field])
            with self.subTest(field=field):
                with self.assertRaisesRegex(SurvivalContractError, "integrity mismatch"):
                    verify_checkpoint(tampered, state=state)

    def test_every_freshness_dimension_is_fail_closed(self) -> None:
        live = FreshnessSeal(HEAD, 11, PROJECTION)
        assert_fresh(FreshnessSeal(HEAD, 11, PROJECTION), live)
        candidates = [
            FreshnessSeal(HEAD2, 11, PROJECTION),
            FreshnessSeal(HEAD, 10, PROJECTION),
            FreshnessSeal(HEAD, 12, PROJECTION),
            FreshnessSeal(HEAD, 11, None),
            FreshnessSeal(HEAD, 11, "sha256:" + "2" * 64),
        ]
        for case, candidate in enumerate(candidates):
            with self.subTest(case=case):
                with self.assertRaises(SurvivalContractError):
                    assert_fresh(candidate, live)

    def test_fencing_generation_never_reuses_after_release(self) -> None:
        registry = ClaimRegistry()
        seal = FreshnessSeal(HEAD, 0, None)
        generations = []
        logical_tick = 1
        for index in range(32):
            claim_id = f"claim-{index}"
            session_id = f"session-{index}"
            record = registry.acquire(
                claim_id=claim_id,
                agent_id="agent",
                session_id=session_id,
                workstream_id="workstream",
                resources=[ResourceAccess("file:state.json", "WRITE")],
                logical_tick=logical_tick,
                ttl_ticks=2,
                local_freshness=seal,
                live_freshness=seal,
            )
            generations.append(record["fencing_generation"])
            registry.validate_writer(
                claim_id,
                session_id=session_id,
                fencing_generation=record["fencing_generation"],
                logical_tick=logical_tick,
            )
            registry.release(claim_id, session_id=session_id)
            logical_tick += 1
        self.assertEqual(generations, list(range(1, 33)))
        self.assertEqual(len(generations), len(set(generations)))

    def test_old_fencing_token_cannot_authorize_new_owner(self) -> None:
        registry = ClaimRegistry()
        seal = FreshnessSeal(HEAD, 0, None)
        first = registry.acquire(
            claim_id="claim-old",
            agent_id="agent-old",
            session_id="session-old",
            workstream_id="w-old",
            resources=[ResourceAccess("tree:src", "WRITE")],
            logical_tick=1,
            ttl_ticks=1,
            local_freshness=seal,
            live_freshness=seal,
        )
        second = registry.acquire(
            claim_id="claim-new",
            agent_id="agent-new",
            session_id="session-new",
            workstream_id="w-new",
            resources=[ResourceAccess("file:src/a.py", "WRITE")],
            logical_tick=3,
            ttl_ticks=5,
            local_freshness=seal,
            live_freshness=seal,
        )
        self.assertGreater(second["fencing_generation"], first["fencing_generation"])
        with self.assertRaises(SurvivalContractError):
            registry.validate_writer(
                "claim-new",
                session_id="session-new",
                fencing_generation=first["fencing_generation"],
                logical_tick=3,
            )


if __name__ == "__main__":
    unittest.main()
