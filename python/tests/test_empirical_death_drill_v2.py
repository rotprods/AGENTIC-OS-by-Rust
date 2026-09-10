from __future__ import annotations

import copy
import unittest

from rot_contracts.empirical_death_drill import verify_empirical_successor_report
from rot_contracts.survival import SurvivalContractError


HEAD = "a" * 40
PROJECT = "rot://project/agentic-os"


def expected_state():
    return {
        "schema_version": "2",
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp8",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": ["rot://workstream/survival"],
        "active_claims": ["rot://claim/survival"],
        "blockers": ["rot://blocker/empirical-drill"],
        "verified_capabilities": ["rot://capability/contracts"],
        "unverified_capabilities": ["rot://capability/empirical-drill"],
        "decisions": [],
        "latest_checkpoint_id": "rot://checkpoint/agentic-os/cp8",
        "projection_hash": None,
        "next_safe_actions": ["execute empirical drill"],
    }


def reconstructed_report(state):
    fields = (
        "project_id", "current_objective_id", "observed_source_sha", "event_watermark",
        "active_workstreams", "active_claims", "blockers", "verified_capabilities",
        "unverified_capabilities", "next_safe_actions",
    )
    return {field: copy.deepcopy(state[field]) for field in fields}


def submission(state, *, elapsed_seconds=45.0):
    return {
        "drill_id": "rot://drill/agentic-os/zero-context/001",
        "runtime_id": "rot://runtime/fresh-successor/test",
        "session_id": "rot://session/fresh-successor/test-001",
        "fresh_context_attestation": True,
        "durable_inputs": [
            "AGENTS.md",
            "STATE.md",
            "TASKS.md",
            "state/project_state.json",
            "state/checkpoints/cp8-structured-error-parity-20260830.json",
        ],
        "forbidden_inputs": [],
        "elapsed_seconds": elapsed_seconds,
        "reconstructed_state": reconstructed_report(state),
    }


class EmpiricalDeathDrillEvidenceContractTests(unittest.TestCase):
    def test_valid_external_submission_can_be_qualified_by_verifier(self):
        state = expected_state()
        result = verify_empirical_successor_report(state, submission(state))
        self.assertTrue(result["passed"])
        self.assertEqual(result["authority"], "EMPIRICALLY_QUALIFIED")
        self.assertTrue(result["fresh_context_attested"])
        self.assertTrue(result["within_slo"])

    def test_test_fixture_does_not_itself_claim_real_world_empirical_execution(self):
        state = expected_state()
        candidate = submission(state)
        candidate["runtime_id"] = "rot://runtime/test-fixture/not-real-qualification"
        result = verify_empirical_successor_report(state, candidate)
        self.assertTrue(result["passed"])
        self.assertEqual(result["runtime_id"], "rot://runtime/test-fixture/not-real-qualification")
        # This unit test proves verifier behavior only. Production state must never consume this
        # fixture as evidence that an independent successor session actually existed.

    def test_missing_fresh_context_attestation_is_rejected(self):
        state = expected_state()
        candidate = submission(state)
        candidate["fresh_context_attestation"] = False
        with self.assertRaises(SurvivalContractError):
            verify_empirical_successor_report(state, candidate)

    def test_any_forbidden_input_is_rejected(self):
        state = expected_state()
        candidate = submission(state)
        candidate["forbidden_inputs"] = ["predecessor-chat-memory"]
        with self.assertRaises(SurvivalContractError):
            verify_empirical_successor_report(state, candidate)

    def test_wrong_reconstructed_state_is_blocked(self):
        state = expected_state()
        candidate = submission(state)
        candidate["reconstructed_state"]["blockers"] = ["rot://blocker/wrong"]
        result = verify_empirical_successor_report(state, candidate)
        self.assertFalse(result["passed"])
        self.assertEqual(result["authority"], "BLOCKED")
        self.assertIn("blockers", result["mismatches"])

    def test_slo_breach_is_blocked_even_with_exact_state(self):
        state = expected_state()
        result = verify_empirical_successor_report(state, submission(state, elapsed_seconds=301.0))
        self.assertFalse(result["passed"])
        self.assertEqual(result["authority"], "BLOCKED")
        self.assertFalse(result["within_slo"])

    def test_empty_durable_input_ledger_is_rejected(self):
        state = expected_state()
        candidate = submission(state)
        candidate["durable_inputs"] = []
        with self.assertRaises(SurvivalContractError):
            verify_empirical_successor_report(state, candidate)


if __name__ == "__main__":
    unittest.main()
