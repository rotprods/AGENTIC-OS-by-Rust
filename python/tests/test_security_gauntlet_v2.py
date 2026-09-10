from __future__ import annotations

import copy
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.context_pack import (
    MAX_CONTEXT_DEPTH,
    MAX_CONTEXT_ITEMS,
    MAX_CONTEXT_STRING_BYTES,
    compile_context_pack,
    verify_context_pack,
)
from rot_contracts.coordination import ClaimRegistry, ResourceAccess
from rot_contracts.promotion import assert_promotion_evidence
from rot_contracts.survival import FreshnessSeal, SurvivalContractError
from rot_contracts.survival_graph import build_survival_projection


HEAD = "a" * 40
CONTRACTS = "sha256:" + "9" * 64
EVIDENCE_HASH = "sha256:" + "7" * 64


def state() -> dict:
    return {
        "project_id": "rot://project/agentic-os",
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/security-gauntlet",
        "observed_source_sha": HEAD,
        "event_watermark": 4,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": ["rot://workstream/survival"],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": [],
        "unverified_capabilities": ["security-gauntlet"],
        "decisions": [],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["execute security gauntlet"],
    }


def claim_snapshot(current: dict) -> dict:
    projection = build_survival_projection(current)
    seal = FreshnessSeal(HEAD, current["event_watermark"], projection["projection_hash"])
    registry = ClaimRegistry()
    registry.acquire(
        claim_id="c1", agent_id="a", session_id="s", workstream_id="w",
        resources=[ResourceAccess("contract:survival", "READ")], logical_tick=1,
        ttl_ticks=10, local_freshness=seal, live_freshness=seal,
    )
    return registry.snapshot(logical_tick=1)


def compile_pack(context: dict) -> tuple[dict, dict, dict, dict]:
    current = state()
    projection = build_survival_projection(current)
    snapshot = claim_snapshot(current)
    packet = compile_context_pack(
        current,
        projection=projection,
        claim_snapshot=snapshot,
        contracts_hash=CONTRACTS,
        session_id="s",
        workstream_id="w",
        relevant_context=context,
    )
    return packet, current, projection, snapshot


def test_record(test_id: str, *, status: str = "PASS", source_sha: str = HEAD,
                run_id: str | None = "run-1", evidence_hash: str | None = EVIDENCE_HASH) -> dict:
    return {
        "test_id": test_id,
        "status": status,
        "source_sha": source_sha,
        "run_id": run_id,
        "evidence_hash": evidence_hash,
    }


class SecurityGauntletV2Tests(unittest.TestCase):
    def test_t12_deep_context_fails_before_recursive_canonicalization(self):
        hostile: dict = {}
        cursor = hostile
        for _ in range(MAX_CONTEXT_DEPTH + 2):
            child: dict = {}
            cursor["x"] = child
            cursor = child
        with self.assertRaisesRegex(SurvivalContractError, "depth"):
            compile_pack(hostile)

    def test_t12_item_fanout_is_bounded(self):
        hostile = {"items": list(range(MAX_CONTEXT_ITEMS + 1))}
        with self.assertRaisesRegex(SurvivalContractError, "item count"):
            compile_pack(hostile)

    def test_t12_individual_string_is_bounded_even_below_total_pack_budget(self):
        hostile = {"payload": "x" * (MAX_CONTEXT_STRING_BYTES + 1)}
        with self.assertRaisesRegex(SurvivalContractError, "string"):
            compile_pack(hostile)

    def test_t12_non_string_mapping_keys_are_rejected(self):
        hostile = {"ok": {1: "not-json-object-semantics"}}
        with self.assertRaisesRegex(SurvivalContractError, "keys must be strings"):
            compile_pack(hostile)

    def test_t12_resealed_hostile_pack_still_fails_structural_validation(self):
        packet, current, projection, snapshot = compile_pack({"safe": True})
        hostile: dict = {}
        cursor = hostile
        for _ in range(MAX_CONTEXT_DEPTH + 2):
            child: dict = {}
            cursor["x"] = child
            cursor = child
        packet["context"] = hostile
        packet.pop("context_pack_hash")
        # hash_canonical is intentionally not called on hostile deeply nested data here:
        # a packet that cannot be safely structurally inspected must never reach hashing.
        packet["context_pack_hash"] = "sha256:" + "0" * 64
        with self.assertRaises(SurvivalContractError):
            verify_context_pack(
                packet, live_state=current, live_projection=projection,
                live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS,
            )

    def test_t14_old_pass_cannot_be_substituted_for_current_candidate(self):
        tests = [test_record("continuity", source_sha="b" * 40)]
        with self.assertRaisesRegex(SurvivalContractError, "different source revision"):
            assert_promotion_evidence(tests, candidate_source_sha=HEAD, required_test_ids=["continuity"])

    def test_t14_required_artifact_binding_can_be_enforced(self):
        tests = [test_record("continuity", evidence_hash=None)]
        with self.assertRaisesRegex(SurvivalContractError, "evidence hash"):
            assert_promotion_evidence(
                tests, candidate_source_sha=HEAD, required_test_ids=["continuity"],
                require_evidence_hash=True,
            )

    def test_t15_cancelled_skipped_failed_and_not_run_never_promote(self):
        for status in ("CANCELLED", "SKIPPED", "FAIL", "NOT_RUN"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(SurvivalContractError, "not PASS"):
                    assert_promotion_evidence(
                        [test_record("continuity", status=status)],
                        candidate_source_sha=HEAD,
                        required_test_ids=["continuity"],
                    )

    def test_t15_missing_or_duplicate_required_result_fails_closed(self):
        with self.assertRaisesRegex(SurvivalContractError, "exactly one"):
            assert_promotion_evidence([], candidate_source_sha=HEAD, required_test_ids=["continuity"])
        duplicate = [test_record("continuity"), test_record("continuity", run_id="run-2")]
        with self.assertRaisesRegex(SurvivalContractError, "exactly one"):
            assert_promotion_evidence(duplicate, candidate_source_sha=HEAD, required_test_ids=["continuity"])

    def test_t16_all_required_checks_must_match_exact_candidate(self):
        tests = [
            test_record("continuity"),
            test_record("rust"),
            test_record("parity", source_sha="b" * 40),
        ]
        with self.assertRaisesRegex(SurvivalContractError, "different source revision"):
            assert_promotion_evidence(
                tests,
                candidate_source_sha=HEAD,
                required_test_ids=["continuity", "rust", "parity"],
            )

    def test_t16_exact_head_complete_evidence_passes(self):
        tests = [
            test_record("continuity", run_id="1"),
            test_record("rust", run_id="2"),
            test_record("parity", run_id="3"),
        ]
        assert_promotion_evidence(
            tests,
            candidate_source_sha=HEAD,
            required_test_ids=["continuity", "rust", "parity"],
            require_evidence_hash=True,
        )

    def test_t13_resealed_context_pack_cannot_promote_its_own_authority(self):
        packet, current, projection, snapshot = compile_pack({"safe": True})
        packet["authority"] = "VERIFIED"
        packet.pop("context_pack_hash")
        packet["context_pack_hash"] = hash_canonical(packet)
        with self.assertRaisesRegex(SurvivalContractError, "authority escalation"):
            verify_context_pack(
                packet, live_state=current, live_projection=projection,
                live_claim_snapshot=snapshot, live_contracts_hash=CONTRACTS,
            )

    def test_t09_fencing_token_from_released_claim_never_revives(self):
        current = state()
        projection = build_survival_projection(current)
        seal = FreshnessSeal(HEAD, current["event_watermark"], projection["projection_hash"])
        registry = ClaimRegistry()
        first = registry.acquire(
            claim_id="old", agent_id="a1", session_id="s1", workstream_id="w1",
            resources=[ResourceAccess("contract:survival", "WRITE")], logical_tick=1,
            ttl_ticks=10, local_freshness=seal, live_freshness=seal,
        )
        registry.release("old", session_id="s1")
        registry.acquire(
            claim_id="new", agent_id="a2", session_id="s2", workstream_id="w2",
            resources=[ResourceAccess("contract:survival", "WRITE")], logical_tick=2,
            ttl_ticks=10, local_freshness=seal, live_freshness=seal,
        )
        with self.assertRaises(SurvivalContractError):
            registry.validate_writer(
                "old", session_id="s1",
                fencing_generation=first["fencing_generation"], logical_tick=2,
            )


if __name__ == "__main__":
    unittest.main()
