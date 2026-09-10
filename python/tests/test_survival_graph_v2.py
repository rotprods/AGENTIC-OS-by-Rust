from __future__ import annotations

import copy
import unittest

from rot_contracts.survival import build_checkpoint, SurvivalContractError
from rot_contracts.survival_graph import build_survival_projection, verify_projection


HEAD = "a" * 40


def state():
    return {
        "project_id": "rot://project/agentic-os",
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp5",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": ["rot://workstream/agentic-os/survival"],
        "active_claims": ["rot://claim/agentic-os/schemas"],
        "blockers": ["rot://blocker/agentic-os/parity"],
        "verified_capabilities": ["rot://capability/f1"],
        "unverified_capabilities": ["rot://capability/death-drill"],
        "decisions": ["rot://decision/agentic-os/projection-one-way"],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["build projection", "run death drill"],
    }


def checkpoint_for(current):
    return build_checkpoint(
        current,
        checkpoint_id="rot://checkpoint/agentic-os/cp5",
        agent_id="rot://agent/openai/architect",
        session_id="rot://session/openai/unique",
        workstream_id="rot://workstream/agentic-os/survival",
        completed=["projection adapter"],
        blockers=["death drill"],
        next_actions=["run death drill"],
        resume_recipe=["verify head", "verify checkpoint", "rebuild projection"],
    )


class SurvivalGraphV2Tests(unittest.TestCase):
    def test_same_state_rebuilds_identical_projection(self):
        current = state()
        cp = checkpoint_for(current)
        a = build_survival_projection(current, checkpoint=cp)
        b = build_survival_projection(copy.deepcopy(current), checkpoint=copy.deepcopy(cp))
        self.assertEqual(a, b)
        self.assertEqual(a["authority"], "DERIVED_PROJECTION_ONLY")
        self.assertTrue(a["projection_hash"].startswith("sha256:"))
        verify_projection(a, current, checkpoint=cp)

    def test_input_order_of_set_like_state_does_not_change_projection(self):
        a = state()
        b = copy.deepcopy(a)
        b["blockers"] = list(reversed(b["blockers"]))
        b["verified_capabilities"] = list(reversed(b["verified_capabilities"]))
        self.assertEqual(build_survival_projection(a), build_survival_projection(b))

    def test_projection_contains_session_checkpoint_and_workstream_lineage(self):
        current = state()
        projection = build_survival_projection(current, checkpoint=checkpoint_for(current))
        edge_triplets = {(e["source"], e["relation"], e["target"]) for e in projection["edges"]}
        self.assertIn(("rot://agent/openai/architect", "HAS_SESSION", "rot://session/openai/unique"), edge_triplets)
        self.assertIn(("rot://session/openai/unique", "EXECUTED", "rot://workstream/agentic-os/survival"), edge_triplets)
        self.assertIn(("rot://blocker/agentic-os/parity", "BLOCKS", "rot://objective/agentic-os/cp5"), edge_triplets)

    def test_projection_is_invalidated_by_state_change(self):
        current = state()
        projection = build_survival_projection(current)
        changed = copy.deepcopy(current)
        changed["blockers"].append("rot://blocker/agentic-os/new")
        with self.assertRaisesRegex(SurvivalContractError, "rebuild mismatch"):
            verify_projection(projection, changed)

    def test_checkpoint_from_different_state_cannot_be_attached(self):
        current = state()
        cp = checkpoint_for(current)
        changed = copy.deepcopy(current)
        changed["blockers"].append("rot://blocker/agentic-os/new")
        with self.assertRaisesRegex(SurvivalContractError, "state binding"):
            build_survival_projection(changed, checkpoint=cp)

    def test_projection_cannot_self_promote_by_mutation(self):
        current = state()
        projection = build_survival_projection(current)
        projection["authority"] = "VERIFIED"
        with self.assertRaisesRegex(SurvivalContractError, "rebuild mismatch"):
            verify_projection(projection, current)

    def test_next_actions_are_advisory_nodes_not_authority(self):
        projection = build_survival_projection(state())
        tasks = [n for n in projection["nodes"] if n["type"] == "Task"]
        self.assertEqual(len(tasks), 2)
        self.assertTrue(all(node["properties"]["authority"] == "ADVISORY" for node in tasks))


if __name__ == "__main__":
    unittest.main()
