from __future__ import annotations

import copy
import unittest

from rot_contracts.death_drill import run_synthetic_death_drill
from rot_contracts.survival import build_checkpoint
from rot_contracts.survival_store import AcceptedEventStore


HEAD = "a" * 40
PROJECT = "rot://project/agentic-os"


def seed():
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp8",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": [],
        "unverified_capabilities": ["zero-context-death-drill"],
        "decisions": ["rot://decision/agentic-os/events-authority"],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["recover from event bundle"],
    }


def event(sequence, event_id, event_type, payload):
    return {"event_id": event_id, "sequence": sequence, "event_type": event_type, "project_id": PROJECT, "payload": payload}


class SyntheticDeathDrillV2Tests(unittest.TestCase):
    def test_agent_death_rebuilds_same_state_and_graph_under_slo(self):
        store = AcceptedEventStore(seed())
        store.append_many([
            event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"}),
            event(2, "e2", "claim.acquired", {"claim_id": "rot://claim/survival"}),
            event(3, "e3", "blocker.added", {"blocker_id": "rot://blocker/external"}),
            event(4, "e4", "next_actions.set", {"next_safe_actions": ["resume safe wave"]}),
        ])
        expected = store.state
        checkpoint = build_checkpoint(
            expected,
            checkpoint_id="rot://checkpoint/agentic-os/death-drill",
            agent_id="rot://agent/openai/predecessor",
            session_id="rot://session/openai/predecessor/dead",
            workstream_id="rot://workstream/survival",
            completed=["persisted recovery bundle"],
            blockers=["rot://blocker/external"],
            next_actions=["resume safe wave"],
            resume_recipe=["verify bundle", "replay accepted events", "rebuild graph"],
        )
        bundle = store.export_recovery_bundle()
        del store
        result = run_synthetic_death_drill(bundle, expected_state=expected, checkpoint=checkpoint)
        self.assertTrue(result["passed"])
        self.assertTrue(result["state_parity"])
        self.assertTrue(result["graph_parity"])
        self.assertEqual(result["authority"], "VERIFIED_SYNTHETIC_RECOVERY")
        self.assertLessEqual(result["elapsed_seconds"], 300)

    def test_oracle_difference_is_detected_even_if_bundle_is_internally_valid(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "blocker.added", {"blocker_id": "b1"}))
        expected = copy.deepcopy(store.state)
        expected["blockers"] = ["different"]
        result = run_synthetic_death_drill(store.export_recovery_bundle(), expected_state=expected)
        self.assertFalse(result["passed"])
        self.assertFalse(result["state_parity"])
        self.assertEqual(result["authority"], "BLOCKED")

    def test_tiny_slo_can_fail_without_corrupting_recovery_semantics(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "next_actions.set", {"next_safe_actions": ["resume"]}))
        expected = store.state
        result = run_synthetic_death_drill(store.export_recovery_bundle(), expected_state=expected, slo_seconds=1e-12)
        self.assertFalse(result["passed"])
        self.assertTrue(result["state_parity"])
        self.assertTrue(result["graph_parity"])
        self.assertEqual(result["authority"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
