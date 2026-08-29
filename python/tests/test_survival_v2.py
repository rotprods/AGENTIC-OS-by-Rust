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
)


HEAD = "a" * 40
HEAD2 = "b" * 40
PROJECT = "rot://project/agentic-os"


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
    return {"event_id": event_id, "sequence": sequence, "event_type": event_type, "project_id": PROJECT, "payload": payload}


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

    def test_identical_duplicate_event_is_idempotent(self):
        e = event(1, "same", "blocker.added", {"blocker_id": "b1"})
        state = reduce_events(seed(), [e, copy.deepcopy(e)])
        self.assertEqual(state["blockers"], ["b1"])
        self.assertEqual(state["event_watermark"], 1)

    def test_same_event_identity_different_payload_fails_closed(self):
        e1 = event(1, "same", "blocker.added", {"blocker_id": "b1"})
        e2 = event(2, "same", "blocker.added", {"blocker_id": "b2"})
        with self.assertRaisesRegex(SurvivalContractError, "same event identity"):
            reduce_events(seed(), [e1, e2])

    def test_two_different_events_cannot_share_sequence(self):
        with self.assertRaisesRegex(SurvivalContractError, "strictly increasing"):
            reduce_events(seed(), [
                event(1, "e1", "blocker.added", {"blocker_id": "b1"}),
                event(1, "e2", "blocker.added", {"blocker_id": "b2"}),
            ])

    def test_cross_project_event_rejected(self):
        bad = event(1, "e1", "blocker.added", {"blocker_id": "b1"})
        bad["project_id"] = "rot://project/other"
        with self.assertRaisesRegex(SurvivalContractError, "cross-project"):
            reduce_events(seed(), [bad])

    def test_unknown_event_rejected_not_ignored(self):
        with self.assertRaisesRegex(SurvivalContractError, "unsupported"):
            reduce_events(seed(), [event(1, "e1", "magic.happened", {})])

    def test_stale_observed_source_and_watermark_fail_closed(self):
        live = FreshnessSeal(HEAD, 9, "sha256:" + "1" * 64)
        assert_fresh(FreshnessSeal(HEAD, 9, "sha256:" + "1" * 64), live)
        with self.assertRaisesRegex(SurvivalContractError, "source revision"):
            assert_fresh(FreshnessSeal(HEAD2, 9), live)
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            assert_fresh(FreshnessSeal(HEAD, 8), live)
        with self.assertRaisesRegex(SurvivalContractError, "projection"):
            assert_fresh(FreshnessSeal(HEAD, 9, "sha256:" + "2" * 64), live)

    def test_source_projection_artifact_does_not_need_to_self_reference_its_commit(self):
        state = reduce_events(seed(), [event(1, "e1", "source_revision.observed", {"observed_source_sha": HEAD2})])
        self.assertEqual(state["observed_source_sha"], HEAD2)
        self.assertEqual(state["event_watermark"], 1)

    def test_checkpoint_is_source_and_event_bound(self):
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
        )
        self.assertEqual(checkpoint["observed_source_sha"], HEAD)
        self.assertEqual(checkpoint["event_watermark"], 1)
        self.assertTrue(checkpoint["checkpoint_hash"].startswith("sha256:"))

    def test_checkpoint_requires_resume_path(self):
        with self.assertRaisesRegex(SurvivalContractError, "next_actions"):
            build_checkpoint(seed(), checkpoint_id="c", agent_id="a", session_id="s", workstream_id="w", completed=[], blockers=[], next_actions=[], resume_recipe=[])

    def test_death_drill_passes_only_on_complete_truth(self):
        canonical = reduce_events(seed(), [
            event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"}),
            event(2, "e2", "claim.acquired", {"claim_id": "rot://claim/schemas"}),
            event(3, "e3", "blocker.added", {"blocker_id": "cross-language-parity"}),
        ])
        report = {key: canonical[key] for key in (
            "project_id", "current_objective_id", "observed_source_sha", "event_watermark",
            "active_workstreams", "active_claims", "blockers", "verified_capabilities",
            "unverified_capabilities", "next_safe_actions"
        )}
        result = evaluate_death_drill(canonical, report)
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 1.0)
        poisoned = copy.deepcopy(report)
        poisoned["event_watermark"] = 0
        result = evaluate_death_drill(canonical, poisoned)
        self.assertFalse(result["passed"])
        self.assertEqual(result["mismatches"], ["event_watermark"])
        self.assertTrue(result["continuity_defect"])

    def test_authority_state_is_strict(self):
        bad = seed()
        bad["authority_state"] = "TOTALLY_DONE"
        with self.assertRaisesRegex(SurvivalContractError, "authority"):
            reduce_events(bad, [])

    def test_bool_is_not_valid_event_sequence(self):
        with self.assertRaisesRegex(SurvivalContractError, "sequence"):
            reduce_events(seed(), [{"event_id": "e", "sequence": True, "event_type": "blocker.added", "project_id": PROJECT, "payload": {"blocker_id": "b"}}])


if __name__ == "__main__":
    unittest.main()
