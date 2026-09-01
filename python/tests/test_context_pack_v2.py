from __future__ import annotations

import copy
import unittest

from rot_contracts.context_pack import compile_context_pack, verify_context_pack, MAX_CONTEXT_CANONICAL_BYTES
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
    def test_pack_is_sealed_untrusted_and_verifies_against_live_bindings(self):
        current = state()
        projection = build_survival_projection(current)
        snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(
            current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS,
            session_id="rot://session/openai/one", workstream_id="rot://workstream/survival",
            relevant_context={"next": ["safe action"], "note": "provider text is data, not instruction"},
        )
        self.assertEqual(packet["authority"], "CACHE_ONLY")
        self.assertEqual(packet["context_trust"], "UNTRUSTED_DATA")
        self.assertTrue(packet["context_pack_hash"].startswith("sha256:"))
        verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_tampered_packet_fails_integrity(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={"x": 1})
        packet["context"]["x"] = 2
        with self.assertRaisesRegex(SurvivalContractError, "integrity"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_missing_trust_label_fails_even_if_resealed(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        from rot_contracts.canonical_json import hash_canonical
        packet.pop("context_trust")
        packet.pop("context_pack_hash")
        packet["context_pack_hash"] = hash_canonical(packet)
        with self.assertRaisesRegex(SurvivalContractError, "trust classification"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_context_budget_is_fail_closed(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        oversized = {"payload": "x" * (MAX_CONTEXT_CANONICAL_BYTES + 1)}
        with self.assertRaisesRegex(SurvivalContractError, "budget"):
            compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context=oversized)

    def test_main_revision_change_invalidates_pack(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        changed = copy.deepcopy(current); changed["observed_source_sha"] = "b" * 40
        with self.assertRaisesRegex(SurvivalContractError, "source revision"):
            verify_context_pack(packet, live_state=changed, live_projection=build_survival_projection(changed), live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_event_watermark_change_invalidates_pack(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        changed = copy.deepcopy(current); changed["event_watermark"] = 5
        with self.assertRaisesRegex(SurvivalContractError, "watermark"):
            verify_context_pack(packet, live_state=changed, live_projection=build_survival_projection(changed), live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)

    def test_claim_snapshot_change_invalidates_pack(self):
        current = state(); projection = build_survival_projection(current); registry = claims(); snapshot = registry.snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        with self.assertRaisesRegex(SurvivalContractError, "claim snapshot"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=registry.snapshot(logical_tick=20), live_contracts_hash=CONTRACTS)

    def test_contract_revision_change_invalidates_pack(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        with self.assertRaisesRegex(SurvivalContractError, "contracts revision"):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash="sha256:" + "8" * 64)

    def test_projection_authority_escalation_never_verifies(self):
        current = state(); projection = build_survival_projection(current); snapshot = claims().snapshot(logical_tick=1)
        packet = compile_context_pack(current, projection=projection, claim_snapshot=snapshot, contracts_hash=CONTRACTS, session_id="s", workstream_id="w", relevant_context={})
        projection["authority"] = "VERIFIED"
        with self.assertRaises(SurvivalContractError):
            verify_context_pack(packet, live_state=current, live_projection=projection, live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS)


if __name__ == "__main__":
    unittest.main()
