from __future__ import annotations

import copy
import unittest

from rot_contracts.context_pack import compile_context_pack, verify_context_pack
from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.survival import FreshnessSeal, SurvivalContractError
from rot_contracts.survival_graph import build_survival_projection


HEAD = "a" * 40
CONTRACTS = "sha256:" + "9" * 64


def state():
    return {
        "project_id": "rot://project/agentic-os",
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp7",
        "observed_source_sha": HEAD,
        "event_watermark": 4,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": ["rot://workstream/survival"],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": ["rot://capability/reducer"],
        "unverified_capabilities": ["rot://capability/context-pack"],
        "decisions": [],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["compile context pack"],
    }


def claims():
    seal = FreshnessSeal(HEAD, 4, build_survival_projection(state())["projection_hash"])
    registry = ClaimRegistry()
    registry.acquire(
        claim_id="c1", agent_id="a", session_id="s", workstream_id="w",
        resources=[ResourceAccess("contract:survival", "READ")], logical_tick=1, ttl_ticks=10,
        local_freshness=seal, live_freshness=seal,
    )
    return registry


class ContextPackV2Tests(unittest.TestCase):
    def test_pack_is_sealed_and_verifies_against_live_bindings(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(
            current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS,
            session_id="rot://session/openai/one", workstream_id="rot://workstream/survival",
            relevant_context={"next": ["safe action"], "note": "UNTRUSTED_DATA"},
        )
        self.assertEqual(packet["authority"], "CACHE_ONLY")
        self.assertTrue(packet["context_pack_hash"].startswith("sha256:"))
        verify_context_pack(
            packet, live_state=current, live_projection=projection,
            live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS,
        )

    def test_tampered_packet_fails_integrity(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={"x": 1})
        packet["context"]["x"] = 2
        with self.assertRaisesRegex(SurvivalContractError, "integrity"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_main_revision_change_invalidates_pack(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        changed = copy.deepcopy(current)
        changed["observed_source_sha"] = "b" * 40
        changed_projection = build_survival_projection(changed)
        with self.assertRaisesRegex(SurvivalContractError, "source revision"):
            verify_context_pack(packet, live_state=changed, live_projection=changed_projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_event_watermark_change_invalidates_pack(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        changed = copy.deepcopy(current)
        changed["event_watermark"] = 5
        changed_projection = build_survival_projection(changed)
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            verify_context_pack(packet, live_state=changed, live_projection=changed_projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_claim_snapshot_change_invalidates_pack(self):
        current = state()
        projection = build_survival_projection(current)
        registry = claims()
        snapshot = registry.snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        changed_snapshot = registry.snapshot(logical_tick=20)
        with self.assertRaisesRegex(SurvivalContractError, "claim snapshot"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=changed_snapshot, live_contracts_hash=CONTRACTS)

    def test_contract_revision_change_invalidates_pack(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        with self.assertRaisesRegex(SurvivalContractError, "contracts revision"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash="sha256:" + "8" * 64)

    def test_projection_authority_escalation_never_verifies(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        projection["authority"] = "VERIFIED"
        with self.assertRaises(SurvivalContractError):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)


if __name__ == "__main__":
    unittest.main()
