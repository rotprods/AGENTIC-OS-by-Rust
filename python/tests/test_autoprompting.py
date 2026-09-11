from __future__ import annotations

import unittest

from rot_ai.autoprompting import compile_next_iteration_metaprompt, render_metaprompt
from rot_ai.hardness import EvidenceRecord, WorkContext

SHA = "c" * 40


class AutoPromptingTests(unittest.TestCase):
    def context(self):
        return WorkContext(
            project_id="rot://project/agentic-os",
            objective_id="rot://objective/hardness-v1",
            repo="rotprods/AGENTIC-OS-by-Rust",
            ref="feat/hardness-v1-self-hosting",
            candidate_sha=SHA,
            risk_classes=("production-critical",),
            requested_level="H5",
            touches_authority=True,
            concurrent_writers_possible=True,
        )

    def compile(self):
        return compile_next_iteration_metaprompt(
            context=self.context(),
            north_star="Self-host the assurance protocol.",
            current_checkpoint="CP-H4",
            blockers=("death-drill-not-run",),
            verified_claims=("compiler deterministic",),
            unverified_claims=("production qualified",),
            tasks=("run gauntlet", "persist exact-head evidence"),
            tests=("unit", "property", "security"),
            evidence=(
                EvidenceRecord("unit", "rotprods/AGENTIC-OS-by-Rust", "feat/hardness-v1-self-hosting", SHA, "PASS", "ev:unit"),
            ),
        )

    def test_packet_is_deterministic(self):
        self.assertEqual(self.compile()["packet_hash"], self.compile()["packet_hash"])

    def test_packet_is_acceleration_not_authority(self):
        packet = self.compile()
        self.assertEqual(packet["authority"], "ACCELERATION_NOT_AUTHORITY")
        self.assertEqual(packet["directive"], "VERIFY LIVE TRUTH BEFORE EXECUTION")

    def test_h5_requirements_propagate(self):
        packet = self.compile()
        self.assertEqual(packet["hardness_level"], "H5")
        self.assertIn("death-drill", packet["required_gates"])
        self.assertIn("promotion", packet["required_gates"])
        self.assertIn("retrospective", packet["lifecycle"]["LEARNING"])

    def test_render_contains_exact_identity(self):
        rendered = render_metaprompt(self.compile())
        self.assertIn(SHA, rendered)
        self.assertIn("VERIFY LIVE TRUTH BEFORE EXECUTION", rendered)
        self.assertIn("Do not claim completion", rendered)

    def test_missing_north_star_rejected(self):
        with self.assertRaisesRegex(ValueError, "north_star"):
            compile_next_iteration_metaprompt(
                context=self.context(),
                north_star="",
                current_checkpoint="CP-H4",
                blockers=(),
                verified_claims=(),
                unverified_claims=(),
                tasks=(),
                tests=(),
            )


if __name__ == "__main__":
    unittest.main()
