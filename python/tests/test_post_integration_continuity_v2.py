from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PostIntegrationContinuityV2Tests(unittest.TestCase):
    def test_consumed_cp15_integration_is_not_reissued_by_live_successor_surfaces(self) -> None:
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        surfaces = [
            "\n".join(state["next_safe_actions"]),
            (ROOT / "STATE.md").read_text(),
            (ROOT / "TASKS.md").read_text(),
            (ROOT / "HANDOFF.md").read_text(),
        ]
        forbidden_imperatives = (
            "integrate the cp15 governance lane",
            "exact-head qualify cp15",
            "use the same native merge mechanism for cp15",
            "integrate cp15 through",
        )
        for surface in surfaces:
            lowered = surface.lower()
            for forbidden in forbidden_imperatives:
                with self.subTest(forbidden=forbidden):
                    self.assertNotIn(forbidden, lowered)

    def test_survival_child_prs_execute_all_three_core_premerge_gates(self) -> None:
        for relative in (
            ".github/workflows/survival-v2-ci.yml",
            ".github/workflows/f1-rust-ci.yml",
            ".github/workflows/f1-parity-ci.yml",
        ):
            with self.subTest(workflow=relative):
                text = (ROOT / relative).read_text()
                pull_request_section = text.split("  push:", 1)[0]
                self.assertIn("pull_request:", pull_request_section)
                self.assertIn("feat/graph-refactor-v2-survival", pull_request_section)


if __name__ == "__main__":
    unittest.main()
