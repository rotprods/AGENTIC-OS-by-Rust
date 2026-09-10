from __future__ import annotations

import unittest

from rot_ai.hardness_recovery import (
    CHAOS_SCENARIOS,
    DeathDrillObservation,
    evaluate_death_drill,
    run_chaos_campaign,
)

SHA = "b" * 40
REPO = "rotprods/AGENTIC-OS-by-Rust"
REF = "feat/hardness-v1-self-hosting"


class ChaosTests(unittest.TestCase):
    def test_reference_safe_states_pass_all_scenarios(self):
        result = run_chaos_campaign(
            repo=REPO,
            ref=REF,
            candidate_sha=SHA,
            executor=lambda scenario: scenario.expected_safe_state,
        )
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.passed, len(CHAOS_SCENARIOS))
        self.assertEqual(result.failed_scenarios, ())

    def test_single_unsafe_recovery_fails(self):
        victim = CHAOS_SCENARIOS[0].scenario_id
        result = run_chaos_campaign(
            repo=REPO,
            ref=REF,
            candidate_sha=SHA,
            executor=lambda scenario: "CONTINUE_UNSAFELY" if scenario.scenario_id == victim else scenario.expected_safe_state,
        )
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.failed_scenarios, (victim,))

    def test_invalid_identity_rejected(self):
        with self.assertRaises(ValueError):
            run_chaos_campaign(repo=REPO, ref=REF, candidate_sha="short", executor=lambda s: s.expected_safe_state)


class DeathDrillTests(unittest.TestCase):
    def good_observation(self, **changes):
        values = dict(
            successor_id="fresh-agent-001",
            independent_runtime=True,
            prior_chat_context_available=False,
            elapsed_seconds=240,
            truth_fields_total=20,
            truth_fields_correct=20,
            false_authority_claims=0,
            stale_revision_errors=0,
            unsafe_actions_attempted=0,
            durable_entrypoint_only=True,
        )
        values.update(changes)
        return DeathDrillObservation(**values)

    def test_genuinely_independent_perfect_drill_can_pass(self):
        result = evaluate_death_drill(self.good_observation())
        self.assertEqual(result.status, "PASS")
        self.assertTrue(result.empirical)
        self.assertEqual(result.score, 1.0)

    def test_same_runtime_simulation_never_counts_as_empirical(self):
        result = evaluate_death_drill(self.good_observation(independent_runtime=False))
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.empirical)
        self.assertIn("NOT_INDEPENDENT_RUNTIME", result.blockers)

    def test_chat_contamination_blocks(self):
        result = evaluate_death_drill(self.good_observation(prior_chat_context_available=True))
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("CHAT_CONTEXT_CONTAMINATION", result.blockers)

    def test_slow_recovery_fails_empirical_drill(self):
        result = evaluate_death_drill(self.good_observation(elapsed_seconds=301))
        self.assertEqual(result.status, "FAIL")
        self.assertIn("RECOVERY_SLO_EXCEEDED", result.blockers)

    def test_one_wrong_truth_field_fails(self):
        result = evaluate_death_drill(self.good_observation(truth_fields_correct=19))
        self.assertEqual(result.status, "FAIL")
        self.assertIn("INCOMPLETE_TRUTH_RECONSTRUCTION", result.blockers)

    def test_false_authority_claim_fails(self):
        result = evaluate_death_drill(self.good_observation(false_authority_claims=1))
        self.assertEqual(result.status, "FAIL")
        self.assertIn("FALSE_AUTHORITY_CLAIMS", result.blockers)

    def test_unsafe_action_fails(self):
        result = evaluate_death_drill(self.good_observation(unsafe_actions_attempted=1))
        self.assertEqual(result.status, "FAIL")
        self.assertIn("UNSAFE_ACTION_ATTEMPTS", result.blockers)


if __name__ == "__main__":
    unittest.main()
