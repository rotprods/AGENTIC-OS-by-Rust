from __future__ import annotations

import unittest

from rot_ai.ggev2_hardness import compile_hardness_projection
from rot_ai.hardness import EvidenceRecord, WorkContext, compile_hardness, evaluate_promotion

SHA = "f" * 40


class GGEV2HardnessProjectionTests(unittest.TestCase):
    def setUp(self):
        self.context = WorkContext(
            project_id="rot://project/agentic-os",
            objective_id="rot://objective/hardness-v1",
            repo="rotprods/AGENTIC-OS-by-Rust",
            ref="feat/hardness-v1-self-hosting",
            candidate_sha=SHA,
            risk_classes=("docs",),
            requested_level="H0",
        )
        self.plan = compile_hardness(self.context)

    def test_projection_is_read_only_and_deterministic(self):
        left = compile_hardness_projection(context=self.context, plan=self.plan, promotion=None, evidence=())
        right = compile_hardness_projection(context=self.context, plan=self.plan, promotion=None, evidence=())
        self.assertEqual(left["projection_hash"], right["projection_hash"])
        self.assertEqual(left["authority"], "DERIVED_READ_ONLY")
        self.assertFalse(left["canonical_mutation_allowed"])
        self.assertFalse(left["projection_can_promote"])

    def test_no_go_is_visible_without_becoming_authority(self):
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=[],
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        projection = compile_hardness_projection(context=self.context, plan=self.plan, promotion=decision, evidence=())
        self.assertEqual(projection["promotion"]["decision"], "NO_GO")
        self.assertTrue(projection["promotion"]["blockers"])
        self.assertFalse(projection["projection_can_promote"])

    def test_go_recommendation_still_cannot_mutate(self):
        evidence = [
            EvidenceRecord(gate, self.context.repo, self.context.ref, SHA, "PASS", f"ev:{gate}")
            for gate in self.plan.required_gates
        ]
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        self.assertEqual(decision.decision, "GO")
        projection = compile_hardness_projection(context=self.context, plan=self.plan, promotion=decision, evidence=evidence)
        self.assertEqual(projection["promotion"]["decision"], "GO")
        self.assertFalse(projection["canonical_mutation_allowed"])
        self.assertFalse(projection["projection_can_promote"])


if __name__ == "__main__":
    unittest.main()
