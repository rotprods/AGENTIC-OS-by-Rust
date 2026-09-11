from __future__ import annotations

import unittest

from rot_ai.ggev2 import compile_realtime_state


PROJECT_STATE = {
    "project_id":"rot://project/agentic-os",
    "north_star":"zero-context recovery",
    "current_objective_id":"rot://objective/cp15",
    "authority_state":"IMPLEMENTED",
    "event_watermark":0,
    "active_workstreams":["rot://workstream/v2"],
    "active_claims":["rot://claim/contracts"],
    "blockers":["rot://blocker/death-drill"],
    "verified_capabilities":["rot://capability/parity"],
    "unverified_capabilities":["rot://capability/durable-writer"],
    "next_safe_actions":["run-death-drill"],
}


class GGEV2Tests(unittest.TestCase):
    def test_semantic_hash_ignores_generation_time(self) -> None:
        kwargs = dict(
            project_state=PROJECT_STATE,
            source_revision="a" * 40,
            source_observations=[{"source_id":"github_live","status":"FRESH","revision":"a" * 40}],
            governance={"status":"BLOCKED"},
            quality_gates={"continuity":"PASS"},
        )
        first = compile_realtime_state(**kwargs, generated_at="2026-09-09T18:00:00Z")
        second = compile_realtime_state(**kwargs, generated_at="2026-09-09T19:00:00Z")
        self.assertNotEqual(first["generated_at"], second["generated_at"])
        self.assertEqual(first["state_hash"], second["state_hash"])

    def test_worst_required_source_status_wins(self) -> None:
        state = compile_realtime_state(
            project_state=PROJECT_STATE,
            source_revision="a" * 40,
            source_observations=[
                {"source_id":"github_live","status":"FRESH","revision":"a" * 40},
                {"source_id":"governance_manifest","status":"BLOCKED","revision":None},
            ],
            governance={},
            quality_gates={},
        )
        self.assertEqual(state["freshness"], "BLOCKED")
        self.assertEqual(state["drift"][0]["source_id"], "governance_manifest")

    def test_graph_uses_shared_ids_and_never_invents_ownership(self) -> None:
        state = compile_realtime_state(
            project_state=PROJECT_STATE,
            source_revision="a" * 40,
            source_observations=[{"source_id":"github_live","status":"FRESH","revision":"a" * 40}],
            governance={},
            quality_gates={},
        )
        node_ids = {node["id"] for node in state["graph"]["nodes"]}
        self.assertIn("rot://claim/contracts", node_ids)
        self.assertIn("rot://blocker/death-drill", node_ids)
        self.assertFalse(any(edge["type"] == "OWNS" for edge in state["graph"]["edges"]))

    def test_missing_observations_fail_closed(self) -> None:
        state = compile_realtime_state(
            project_state=PROJECT_STATE,
            source_revision="a" * 40,
            source_observations=[],
            governance={},
            quality_gates={},
        )
        self.assertEqual(state["freshness"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
