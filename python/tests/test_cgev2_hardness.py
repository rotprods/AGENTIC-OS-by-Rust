from __future__ import annotations

import unittest

from rot_ai.cgev2_hardness import CGEV2Task, compile_cgev2_hardness

SHA = "9" * 40


class CGEV2HardnessTests(unittest.TestCase):
    def task(self, **overrides):
        values = dict(
            task_id="TASK-HARDNESS-001",
            project_id="rot://project/agentic-os",
            objective_id="rot://objective/hardness-v1",
            north_star="Compile safe agentic execution.",
            checkpoint="CP-H6",
            repo="rotprods/AGENTIC-OS-by-Rust",
            ref="feat/hardness-v1-self-hosting",
            candidate_sha=SHA,
            risk_classes=("production-critical",),
            touches_authority=True,
            concurrent_writers_possible=True,
            tasks=("execute wave",),
            tests=("run exact-head gates",),
        )
        values.update(overrides)
        return CGEV2Task(**values)

    def test_shadow_compiles_h5_without_canonical_mutation(self):
        result = compile_cgev2_hardness(self.task(), enforcement_mode="SHADOW")
        self.assertEqual(result["hardness_level"], "H5")
        self.assertEqual(result["enforcement_mode"], "SHADOW")
        self.assertFalse(result["canonical_mutation_allowed"])
        self.assertFalse(result["enforced_block"])
        self.assertEqual(result["next_iteration_packet"]["directive"], "VERIFY LIVE TRUTH BEFORE EXECUTION")

    def test_unknown_risk_is_visible_in_shadow(self):
        result = compile_cgev2_hardness(self.task(risk_classes=("unknown-new-risk",)), enforcement_mode="SHADOW")
        self.assertTrue(result["would_block"])
        self.assertFalse(result["enforced_block"])
        self.assertIn("UNKNOWN_RISK:unknown-new-risk", result["hardness_blockers"])

    def test_unknown_risk_blocks_in_enforce_mode(self):
        result = compile_cgev2_hardness(self.task(risk_classes=("unknown-new-risk",)), enforcement_mode="ENFORCE")
        self.assertTrue(result["would_block"])
        self.assertTrue(result["enforced_block"])

    def test_compilation_is_deterministic(self):
        left = compile_cgev2_hardness(self.task())
        right = compile_cgev2_hardness(self.task())
        self.assertEqual(left["compilation_hash"], right["compilation_hash"])

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            compile_cgev2_hardness(self.task(), enforcement_mode="MAGIC")


if __name__ == "__main__":
    unittest.main()
