from __future__ import annotations

import copy
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.survival import (
    FreshnessSeal,
    SurvivalContractError,
    assert_fresh,
    build_checkpoint,
    evaluate_death_drill,
    reduce_events,
    verify_checkpoint,
)


HEAD = "a" * 40
HEAD2 = "b" * 40
PROJECT = "rot://project/agentic-os"
PROJECTION = "sha256:" + "1" * 64


def seed():
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp4",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": [],
        "unverified_capabilities": ["survival-reducer"],
        "decisions": [],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["run-survival-tests"],
    }


def event(sequence, event_id, event_type, payload):
    return {
        "event_id": event_id,
        "sequence": sequence,
        "event_type": event_type,
        "project_id": PROJECT,
        "payload": payload,
    }


def report_for(state):
    return {key: state[key] for key in (
        "project_id", "current_objective_id", "observed_source_sha", "event_watermark",
        "active_workstreams", "active_claims", "blockers", "verified_capabilities",
        "unverified_capabilities", "next_safe_actions",
    )}


class SurvivalReducerTests(unittest.TestCase):
    def test_replay_is_deterministic_independent_of_input_order(self):
        events = [
            event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"}),
            event(2, "e2", "claim.acquired", {"claim_id": "rot://claim/survival-schema"}),
            event(3, "e3", "capability.verified", {"capability_id": "survival-reducer"}),
            event(4, "e4", "next_actions.set", {"next_safe_actions": ["build-cos-projection"]}),
        ]
        a = reduce_events(seed(), events)
        b = reduce_events(seed(), list(reversed(events)))
        self.assertEqual(a, b)
        self.assertEqual(hash_canonical(a), hash_canonical(b))
        self.assertEqual(a["event_watermark"], 4)
        self.assertEqual(a["verified_capabilities"], ["survival-reducer"])

    def test_identical_duplicate_event_is_idempotent_within_batch(self):
        e = event(1, "same", "blocker.added", {"blocker_id": "b1"})
        state = reduce_events(seed(), [e, copy.deepcopy(e)])
        self.assertEqual(state["blockers"], ["b1"])
        self.assertEqual(state["event_watermark"], 1)

    def test_same_event_identity_different_payload_fails_closed(self):
        with self.assertRaisesRegex(SurvivalContractError, "same event identity"):
            reduce_events(seed(), [
                event(1, "same", "blocker.added", {"blocker_id": "b1"}),
                event(2, "same", "blocker.added", {"blocker_id": "b2"}),
            ])

    def test_two_different_events_cannot_share_sequence(self):
        with self.assertRaisesRegex(SurvivalContractError, "discontinuity"):
            reduce_events(seed(), [
                event(1, "e1", "blocker.added", {"blocker_id": "b1"}),
                event(1, "e2", "blocker.added", {"blocker_id": "b2"}),
            ])

    def test_event_sequence_cannot_have_hidden_gap(self):
        with self.assertRaisesRegex(SurvivalContractError, "expected 2, got 3"):
            reduce_events(seed(), [
                event(1, "e1", "blocker.added", {"blocker_id": "b1"}),
                event(3, "e3", "blocker.added", {"blocker_id": "b3"}),
            ])

    def test_incremental_replay_requires_next_contiguous_sequence(self):
        current = seed()
        current["event_watermark"] = 5
        for sequence in (4, 5, 7):
            with self.assertRaisesRegex(SurvivalContractError, "discontinuity"):
                reduce_events(current, [event(sequence, f"e{sequence}", "blocker.added", {"blocker_id": "b"})])
        advanced = reduce_events(current, [event(6, "e6", "blocker.added", {"blocker_id": "b"})])
        self.assertEqual(advanced["event_watermark"], 6)

    def test_cross_project_event_rejected(self):
        bad = event(1, "e1", "blocker.added", {"blocker_id": "b1"})
        bad["project_id"] = "rot://project/other"
        with self.assertRaisesRegex(SurvivalContractError, "cross-project"):
            reduce_events(seed(), [bad])

    def test_unknown_event_rejected_not_ignored(self):
        with self.assertRaisesRegex(SurvivalContractError, "unsupported"):
            reduce_events(seed(), [event(1, "e1", "magic.happened", {})])

    def test_freshness_fails_on_source_watermark_or_projection_mismatch(self):
        live = FreshnessSeal(HEAD, 9, PROJECTION)
        assert_fresh(FreshnessSeal(HEAD, 9, PROJECTION), live)
        with self.assertRaisesRegex(SurvivalContractError, "source revision"):
            assert_fresh(FreshnessSeal(HEAD2, 9, PROJECTION), live)
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            assert_fresh(FreshnessSeal(HEAD, 8, PROJECTION), live)
        with self.assertRaisesRegex(SurvivalContractError, "projection"):
            assert_fresh(FreshnessSeal(HEAD, 9, "sha256:" + "2" * 64), live)

    def test_known_projection_cannot_be_ignored_by_omission(self):
        with self.assertRaisesRegex(SurvivalContractError, "projection"):
            assert_fresh(FreshnessSeal(HEAD, 9, None), FreshnessSeal(HEAD, 9, PROJECTION))
        with self.assertRaisesRegex(SurvivalContractError, "projection"):
            assert_fresh(FreshnessSeal(HEAD, 9, PROJECTION), FreshnessSeal(HEAD, 9, None))

    def test_source_projection_artifact_does_not_need_to_self_reference_its_commit(self):
        state = reduce_events(seed(), [event(1, "e1", "source_revision.observed", {"observed_source_sha": HEAD2})])
        self.assertEqual(state["observed_source_sha"], HEAD2)
        self.assertEqual(state["event_watermark"], 1)

    def test_checkpoint_is_state_source_event_bound_and_tamper_evident(self):
        state = reduce_events(seed(), [event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"})])
        checkpoint = build_checkpoint(
            state,
            checkpoint_id="rot://checkpoint/agentic-os/cp4",
            agent_id="rot://agent/chatgpt/architect",
            session_id="rot://session/chatgpt/unique",
            workstream_id="rot://workstream/survival",
            completed=["reference reducer"],
            blockers=[],
            next_actions=["run death drill"],
            resume_recipe=["read AGENTS", "verify observed source", "replay events"],
            tests=[{"test_id": "survival-unit", "status": "PASS", "source_sha": HEAD}],
        )
        self.assertEqual(checkpoint["state_hash"], hash_canonical(state))
        verify_checkpoint(checkpoint, state=state)
        tampered = copy.deepcopy(checkpoint)
        tampered["completed"].append("not actually done")
        with self.assertRaisesRegex(SurvivalContractError, "integrity mismatch"):
            verify_checkpoint(tampered, state=state)

    def test_checkpoint_rejects_different_state_even_if_document_hash_is_valid(self):
        checkpoint = build_checkpoint(
            seed(), checkpoint_id="c", agent_id="a", session_id="s", workstream_id="w",
            completed=[], blockers=[], next_actions=["n"], resume_recipe=["r"],
        )
        changed = seed()
        changed["blockers"] = ["new-blocker"]
        with self.assertRaisesRegex(SurvivalContractError, "state binding"):
            verify_checkpoint(checkpoint, state=changed)

    def test_checkpoint_requires_resume_path_and_strict_test_evidence(self):
        with self.assertRaisesRegex(SurvivalContractError, "next_actions"):
            build_checkpoint(seed(), checkpoint_id="c", agent_id="a", session_id="s", workstream_id="w", completed=[], blockers=[], next_actions=[], resume_recipe=[])
        with self.assertRaisesRegex(SurvivalContractError, "test status"):
            build_checkpoint(
                seed(), checkpoint_id="c", agent_id="a", session_id="s", workstream_id="w",
                completed=[], blockers=[], next_actions=["n"], resume_recipe=["r"],
                tests=[{"test_id": "t", "status": "GREENISH", "source_sha": HEAD}],
            )

    def test_death_drill_requires_truth_and_slo(self):
        canonical = reduce_events(seed(), [
            event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"}),
            event(2, "e2", "claim.acquired", {"claim_id": "rot://claim/schemas"}),
            event(3, "e3", "blocker.added", {"blocker_id": "cross-language-parity"}),
        ])
        report = report_for(canonical)
        result = evaluate_death_drill(canonical, report, elapsed_seconds=299.9)
        self.assertTrue(result["passed"])
        self.assertTrue(result["within_slo"])
        self.assertEqual(result["score"], 1.0)

        slow = evaluate_death_drill(canonical, report, elapsed_seconds=300.1)
        self.assertFalse(slow["passed"])
        self.assertFalse(slow["within_slo"])
        self.assertTrue(slow["continuity_defect"])

        poisoned = copy.deepcopy(report)
        poisoned["event_watermark"] = 0
        result = evaluate_death_drill(canonical, poisoned, elapsed_seconds=10)
        self.assertFalse(result["passed"])
        self.assertEqual(result["mismatches"], ["event_watermark"])

    def test_death_drill_elapsed_time_is_not_agent_text(self):
        canonical = seed()
        report = report_for(canonical)
        report["elapsed_seconds"] = 1
        result = evaluate_death_drill(canonical, report, elapsed_seconds=301)
        self.assertFalse(result["passed"])
        self.assertFalse(result["within_slo"])

    def test_death_drill_rejects_wrong_collection_type_as_mismatch(self):
        canonical = seed()
        report = report_for(canonical)
        report["active_workstreams"] = "rot://workstream/survival"
        result = evaluate_death_drill(canonical, report, elapsed_seconds=5)
        self.assertFalse(result["passed"])
        self.assertIn("active_workstreams", result["mismatches"])

    def test_authority_state_is_strict(self):
        bad = seed()
        bad["authority_state"] = "TOTALLY_DONE"
        with self.assertRaisesRegex(SurvivalContractError, "authority"):
            reduce_events(bad, [])

    def test_bool_is_not_valid_event_sequence_watermark_or_elapsed_time(self):
        with self.assertRaisesRegex(SurvivalContractError, "sequence"):
            reduce_events(seed(), [{"event_id": "e", "sequence": True, "event_type": "blocker.added", "project_id": PROJECT, "payload": {"blocker_id": "b"}}])
        bad = seed()
        bad["event_watermark"] = True
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            reduce_events(bad, [])
        with self.assertRaisesRegex(SurvivalContractError, "elapsed_seconds"):
            evaluate_death_drill(seed(), report_for(seed()), elapsed_seconds=True)


if __name__ == "__main__":
    unittest.main()
