from __future__ import annotations

import unittest

from rot_ai.ggev2_swarm import SwarmTelemetryError, TelemetryEvent, compile_swarm

SHA_A = "a" * 40
SHA_B = "b" * 40


def event(kind: str, *, agent: str = "agent:a", session: str = "session:1", claim: str | None = None, head: str = SHA_A, resources=(), semantics=(), watermark=None, evidence=(), next_action=None, fencing=None):
    return TelemetryEvent(
        event_type=kind,
        agent_id=agent,
        session_id=session,
        project_id="project:p",
        objective_id="objective:o",
        repo="rotprods/repo",
        branch="feat/x",
        head_sha=head,
        observed_at=f"2026-09-09T21:3{len(kind)}:00Z",
        workstream_id="workstream:w",
        claim_id=claim,
        fencing_generation=fencing,
        event_watermark=watermark,
        state_hash="sha256:" + "1" * 64 if watermark is not None else None,
        semantic_scopes=tuple(semantics),
        resource_scopes=tuple(resources),
        evidence_ids=tuple(evidence),
        next_action=next_action,
        freshness="FRESH",
    )


class SwarmTests(unittest.TestCase):
    def test_compile_session_and_claim(self) -> None:
        output = compile_swarm([
            event("BOOT"),
            event("CLAIM", claim="claim:1", fencing=1, resources=("file:a",)),
            event("HEARTBEAT", watermark=4),
            event("EVIDENCE", evidence=("evidence:1",)),
            event("HANDOFF", next_action="continue"),
        ], current_heads={"rotprods/repo": SHA_A})
        self.assertEqual(output["stale_sessions"], [])
        self.assertEqual(len(output["claims"]), 1)
        self.assertEqual(output["sessions"][0]["latest_watermark"], 4)
        self.assertEqual(output["authority_class"], "DERIVED_OBSERVATION_ONLY")

    def test_stale_head_detected(self) -> None:
        output = compile_swarm([event("BOOT", head=SHA_B)], current_heads={"rotprods/repo": SHA_A})
        self.assertEqual(output["stale_sessions"], ["session:1"])

    def test_resource_collision_detected(self) -> None:
        output = compile_swarm([
            event("CLAIM", agent="agent:a", session="session:a", claim="claim:a", fencing=1, resources=("file:same",)),
            event("CLAIM", agent="agent:b", session="session:b", claim="claim:b", fencing=2, resources=("file:same",)),
        ], current_heads={"rotprods/repo": SHA_A})
        self.assertEqual(output["collisions"][0]["severity"], "P1")

    def test_semantic_collision_detected(self) -> None:
        output = compile_swarm([
            event("CLAIM", agent="agent:a", session="session:a", claim="claim:a", fencing=1, semantics=("identity",)),
            event("CLAIM", agent="agent:b", session="session:b", claim="claim:b", fencing=2, semantics=("identity",)),
        ], current_heads={"rotprods/repo": SHA_A})
        self.assertEqual(output["collisions"][0]["severity"], "P2")

    def test_watermark_regression_rejected(self) -> None:
        with self.assertRaisesRegex(SwarmTelemetryError, "watermark regression"):
            compile_swarm([event("HEARTBEAT", watermark=5), event("HEARTBEAT", watermark=4)], current_heads={"rotprods/repo": SHA_A})

    def test_claim_requires_fencing(self) -> None:
        with self.assertRaisesRegex(SwarmTelemetryError, "CLAIM requires"):
            compile_swarm([event("CLAIM", claim="claim:1")], current_heads={"rotprods/repo": SHA_A})

    def test_session_identity_collision_rejected(self) -> None:
        with self.assertRaisesRegex(SwarmTelemetryError, "session identity collision"):
            compile_swarm([event("BOOT", agent="agent:a"), event("BOOT", agent="agent:b")], current_heads={"rotprods/repo": SHA_A})


if __name__ == "__main__":
    unittest.main()
