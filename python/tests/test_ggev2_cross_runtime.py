from __future__ import annotations

import copy
import unittest

from rot_ai.ggev2_cross_runtime import CrossRuntimeIngestError, compile_cross_runtime


SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


def observation(*, repo: str, branch: str, sha: str, agent: str, session: str, authority_key: str = "authority", observed_at: str = "2026-09-10T00:00:00Z") -> dict:
    value = {
        "schema_version": "1",
        "event_type": "HEARTBEAT",
        "agent_id": agent,
        "session_id": session,
        "project_id": "PROJECT",
        "objective_id": "OBJECTIVE",
        "workstream_id": "WORKSTREAM",
        "repo": repo,
        "branch": branch,
        "head_sha": sha,
        "event_watermark": 1,
        "resource_scopes": [],
        "semantic_scopes": [],
        "evidence_ids": [],
        "observed_at": observed_at,
    }
    value[authority_key] = "OBSERVATION_ONLY"
    return value


class CrossRuntimeTests(unittest.TestCase):
    def test_three_runtime_formats_compile_without_authority(self) -> None:
        a = observation(repo="rotprods/AGENTIC-OS-by-Rust", branch="feat/ggev2-r3-live-swarm", sha=SHA_A, agent="agent-a", session="session-a", authority_key="authority_class")
        b = observation(repo="rotprods/mission-control", branch="feat/ggev2-r3-telemetry-emitter", sha=SHA_B, agent="agent-b", session="session-b")
        c = observation(repo="rotprods/cos-graph-engine", branch="feat/ggev2-r3-telemetry-emitter", sha=SHA_C, agent="agent-c", session="session-c")
        out = compile_cross_runtime(
            [
                {"runtime_id": "agentic-os", "observations": [a]},
                {"runtime_id": "mission-control", "observations": [b]},
                {"runtime_id": "cos-graph-engine", "observations": [c]},
            ],
            current_heads={a["repo"]: SHA_A, b["repo"]: SHA_B, c["repo"]: SHA_C},
        )
        self.assertEqual(out["status"], "COMPILED")
        self.assertEqual(out["runtime_ids"], ["agentic-os", "cos-graph-engine", "mission-control"])
        self.assertEqual(out["unique_observations"], 3)
        self.assertEqual(out["swarm"]["authority_class"], "DERIVED_OBSERVATION_ONLY")
        self.assertFalse(out["promotion_authority"])
        self.assertFalse(out["accepted_event_authority"])

    def test_exact_replay_duplicate_is_suppressed(self) -> None:
        event = observation(repo="rotprods/mission-control", branch="feat/x", sha=SHA_A, agent="agent", session="session")
        out = compile_cross_runtime(
            [{"runtime_id": "mission-control", "observations": [event, copy.deepcopy(event)]}],
            current_heads={event["repo"]: SHA_A},
        )
        self.assertEqual(out["observations_seen"], 2)
        self.assertEqual(out["unique_observations"], 1)
        self.assertEqual(out["exact_duplicates_suppressed"], 1)

    def test_same_runtime_identity_with_different_content_fails_closed(self) -> None:
        first = observation(repo="rotprods/mission-control", branch="feat/x", sha=SHA_A, agent="agent", session="session")
        second = copy.deepcopy(first)
        second["head_sha"] = SHA_B
        out = compile_cross_runtime(
            [{"runtime_id": "mission-control", "observations": [first, second]}],
            current_heads={first["repo"]: SHA_B},
        )
        self.assertEqual(out["status"], "COLLISION_BLOCKED")
        self.assertIsNone(out["swarm"])
        self.assertEqual(len(out["conflicts"]), 1)
        self.assertEqual(out["conflicts"][0]["authority_effect"], "NONE")

    def test_replay_hash_is_deterministic_across_batch_order(self) -> None:
        a = observation(repo="rotprods/a", branch="main", sha=SHA_A, agent="a", session="sa", authority_key="authority_class")
        b = observation(repo="rotprods/b", branch="main", sha=SHA_B, agent="b", session="sb")
        one = compile_cross_runtime(
            [{"runtime_id": "a-runtime", "observations": [a]}, {"runtime_id": "b-runtime", "observations": [b]}],
            current_heads={"rotprods/a": SHA_A, "rotprods/b": SHA_B},
        )
        two = compile_cross_runtime(
            [{"runtime_id": "b-runtime", "observations": [b]}, {"runtime_id": "a-runtime", "observations": [a]}],
            current_heads={"rotprods/a": SHA_A, "rotprods/b": SHA_B},
        )
        self.assertEqual(one["cross_runtime_hash"], two["cross_runtime_hash"])

    def test_non_observation_authority_is_rejected(self) -> None:
        event = observation(repo="rotprods/a", branch="main", sha=SHA_A, agent="a", session="sa")
        event["authority"] = "CANONICAL"
        with self.assertRaisesRegex(CrossRuntimeIngestError, "OBSERVATION_ONLY"):
            compile_cross_runtime([{"runtime_id": "runtime", "observations": [event]}], current_heads={})


if __name__ == "__main__":
    unittest.main()
