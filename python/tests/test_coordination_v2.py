from __future__ import annotations

import unittest

from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.survival import FreshnessSeal, SurvivalContractError


HEAD = "a" * 40
SEAL = FreshnessSeal(HEAD, 7, "sha256:" + "1" * 64)


class CoordinationV2Tests(unittest.TestCase):
    def test_read_read_overlap_is_allowed(self):
        registry = ClaimRegistry()
        registry.acquire(claim_id="c1", agent_id="a1", session_id="s1", workstream_id="w1", resources=[ResourceAccess("tree:src", "READ")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)
        registry.acquire(claim_id="c2", agent_id="a2", session_id="s2", workstream_id="w2", resources=[ResourceAccess("file:src/a.py", "READ")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)

    def test_tree_write_conflicts_with_nested_file_write(self):
        registry = ClaimRegistry()
        registry.acquire(claim_id="c1", agent_id="a1", session_id="s1", workstream_id="w1", resources=[ResourceAccess("tree:src", "WRITE")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)
        with self.assertRaisesRegex(SurvivalContractError, "scope conflict"):
            registry.acquire(claim_id="c2", agent_id="a2", session_id="s2", workstream_id="w2", resources=[ResourceAccess("file:src/a.py", "WRITE")], logical_tick=2, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)

    def test_unrelated_writes_can_proceed(self):
        registry = ClaimRegistry()
        registry.acquire(claim_id="c1", agent_id="a1", session_id="s1", workstream_id="w1", resources=[ResourceAccess("file:src/a.py", "WRITE")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)
        registry.acquire(claim_id="c2", agent_id="a2", session_id="s2", workstream_id="w2", resources=[ResourceAccess("file:docs/a.md", "WRITE")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)

    def test_expired_claim_can_be_taken_over_with_higher_generation(self):
        registry = ClaimRegistry()
        old = registry.acquire(claim_id="c1", agent_id="a1", session_id="s1", workstream_id="w1", resources=[ResourceAccess("contract:event", "WRITE")], logical_tick=1, ttl_ticks=2, local_freshness=SEAL, live_freshness=SEAL)
        new = registry.acquire(claim_id="c2", agent_id="a2", session_id="s2", workstream_id="w2", resources=[ResourceAccess("contract:event", "WRITE")], logical_tick=4, ttl_ticks=2, local_freshness=SEAL, live_freshness=SEAL)
        self.assertGreater(new["fencing_generation"], old["fencing_generation"])
        with self.assertRaisesRegex(SurvivalContractError, "expired"):
            registry.validate_writer("c1", session_id="s1", fencing_generation=old["fencing_generation"], logical_tick=4)
        registry.validate_writer("c2", session_id="s2", fencing_generation=new["fencing_generation"], logical_tick=4)

    def test_release_never_resets_fencing_generation(self):
        registry = ClaimRegistry()
        first = registry.acquire(claim_id="c1", agent_id="a1", session_id="s1", workstream_id="w1", resources=[ResourceAccess("schema:event", "WRITE")], logical_tick=1, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)
        registry.release("c1", session_id="s1")
        second = registry.acquire(claim_id="c2", agent_id="a2", session_id="s2", workstream_id="w2", resources=[ResourceAccess("schema:event", "WRITE")], logical_tick=2, ttl_ticks=10, local_freshness=SEAL, live_freshness=SEAL)
        self.assertGreater(second["fencing_generation"], first["fencing_generation"])

    def test_stale_freshness_cannot_acquire_claim(self):
        registry = ClaimRegistry()
        stale = FreshnessSeal(HEAD, 6, SEAL.projection_hash)
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            registry.acquire(claim_id="c1", agent_id="a", session_id="s", workstream_id="w", resources=[ResourceAccess("plan:v2", "WRITE")], logical_tick=1, ttl_ticks=3, local_freshness=stale, live_freshness=SEAL)

    def test_read_only_claim_cannot_authorize_writer(self):
        registry = ClaimRegistry()
        claim = registry.acquire(claim_id="c1", agent_id="a", session_id="s", workstream_id="w", resources=[ResourceAccess("file:README.md", "READ")], logical_tick=1, ttl_ticks=3, local_freshness=SEAL, live_freshness=SEAL)
        with self.assertRaisesRegex(SurvivalContractError, "read-only"):
            registry.validate_writer("c1", session_id="s", fencing_generation=claim["fencing_generation"], logical_tick=1)

    def test_path_traversal_scope_is_rejected(self):
        with self.assertRaisesRegex(SurvivalContractError, "resource scope"):
            ResourceAccess("file:src/../secret", "WRITE")

    def test_snapshot_marks_expired_claim_without_rewriting_history(self):
        registry = ClaimRegistry()
        registry.acquire(claim_id="c1", agent_id="a", session_id="s", workstream_id="w", resources=[ResourceAccess("file:a", "WRITE")], logical_tick=1, ttl_ticks=1, local_freshness=SEAL, live_freshness=SEAL)
        snapshot = registry.snapshot(logical_tick=3)
        self.assertEqual(snapshot["claims"][0]["status"], "ACTIVE")
        self.assertEqual(snapshot["claims"][0]["effective_status"], "EXPIRED")
        self.assertTrue(snapshot["snapshot_hash"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
