from __future__ import annotations

import unittest

from rot_ai.hardness import WorkContext
from rot_ai.hardness_assurance import (
    POLICY_MUTANTS,
    result_as_json,
    run_deterministic_fuzz_campaign,
    run_policy_mutation_campaign,
)

SHA = "a" * 40


def context() -> WorkContext:
    return WorkContext(
        project_id="rot://project/agentic-os",
        objective_id="rot://objective/hardness-v1",
        repo="rotprods/AGENTIC-OS-by-Rust",
        ref="feat/hardness-v1-self-hosting",
        candidate_sha=SHA,
        risk_classes=("production-critical",),
        requested_level="H5",
    )


class MutationCampaignTests(unittest.TestCase):
    def test_all_registered_critical_mutants_are_killed_by_reference_oracle(self):
        killed = {mutant.mutant_id for mutant in POLICY_MUTANTS}
        result = run_policy_mutation_campaign(context=context(), oracle=lambda mutant: mutant.mutant_id in killed)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.total, len(POLICY_MUTANTS))
        self.assertEqual(result.killed, len(POLICY_MUTANTS))
        self.assertEqual(result.critical_survivors, ())
        self.assertEqual(result.score, 1.0)

    def test_critical_survivor_fails_campaign_even_with_high_score(self):
        survivor = POLICY_MUTANTS[0].mutant_id
        result = run_policy_mutation_campaign(context=context(), oracle=lambda mutant: mutant.mutant_id != survivor)
        self.assertEqual(result.status, "FAIL")
        self.assertIn(survivor, result.critical_survivors)
        self.assertLess(result.score, 1.0)

    def test_budget_is_bounded(self):
        with self.assertRaises(ValueError):
            run_policy_mutation_campaign(context=context(), oracle=lambda _: True, max_mutants=0)
        with self.assertRaises(ValueError):
            run_policy_mutation_campaign(context=context(), oracle=lambda _: True, max_mutants=257)

    def test_mutation_evidence_is_revision_bound(self):
        result = run_policy_mutation_campaign(context=context(), oracle=lambda _: True)
        self.assertEqual(result.repo, context().repo)
        self.assertEqual(result.ref, context().ref)
        self.assertEqual(result.candidate_sha, SHA)
        self.assertTrue(result.evidence_hash.startswith("sha256:"))


class FuzzCampaignTests(unittest.TestCase):
    def test_campaign_is_deterministic_and_green(self):
        left = run_deterministic_fuzz_campaign(context=context(), seed=20260910, iterations=2000)
        right = run_deterministic_fuzz_campaign(context=context(), seed=20260910, iterations=2000)
        self.assertEqual(left, right)
        self.assertEqual(left.status, "PASS")
        self.assertEqual(left.failures, ())

    def test_different_seed_is_recorded_for_replay(self):
        first = run_deterministic_fuzz_campaign(context=context(), seed=1, iterations=50)
        second = run_deterministic_fuzz_campaign(context=context(), seed=2, iterations=50)
        self.assertEqual(first.seed, 1)
        self.assertEqual(second.seed, 2)
        self.assertNotEqual(first.evidence_hash, second.evidence_hash)

    def test_fuzz_budget_rejects_unbounded_campaign(self):
        with self.assertRaises(ValueError):
            run_deterministic_fuzz_campaign(context=context(), seed=1, iterations=0)
        with self.assertRaises(ValueError):
            run_deterministic_fuzz_campaign(context=context(), seed=1, iterations=100001)

    def test_evidence_json_is_stable(self):
        result = run_deterministic_fuzz_campaign(context=context(), seed=42, iterations=100)
        self.assertEqual(result_as_json(result), result_as_json(result))
        self.assertIn('"authority":"EVIDENCE_ONLY"', result_as_json(result))


if __name__ == "__main__":
    unittest.main()
