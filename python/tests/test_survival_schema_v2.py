from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]


def load(name: str):
    return json.loads((ROOT / "schemas" / name).read_text())


class SurvivalSchemaV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state_validator = Draft202012Validator(load("survival-project-state.v2.schema.json"), format_checker=FormatChecker())
        cls.checkpoint_validator = Draft202012Validator(load("survival-checkpoint.v2.schema.json"), format_checker=FormatChecker())

    def test_valid_state(self):
        state = {
            "schema_version": "2",
            "project_id": "rot://project/agentic-os",
            "north_star": "zero-context recovery",
            "current_objective_id": "rot://objective/agentic-os/cp4",
            "observed_source_sha": "a" * 40,
            "event_watermark": 1,
            "authority_state": "IMPLEMENTED",
            "active_workstreams": ["rot://workstream/survival"],
            "active_claims": [],
            "blockers": ["cross-language-parity"],
            "verified_capabilities": [],
            "unverified_capabilities": ["survival-reducer"],
            "next_safe_actions": ["run clean CI"],
        }
        self.assertEqual(list(self.state_validator.iter_errors(state)), [])

    def test_state_rejects_unknown_authority_and_extra_fields(self):
        state = {
            "schema_version": "2", "project_id": "p", "north_star": "n", "current_objective_id": "o",
            "observed_source_sha": "a" * 40, "event_watermark": 0, "authority_state": "DONE",
            "active_workstreams": [], "active_claims": [], "blockers": [], "verified_capabilities": [],
            "unverified_capabilities": [], "next_safe_actions": ["x"], "secret_extra": True,
        }
        errors = list(self.state_validator.iter_errors(state))
        self.assertGreaterEqual(len(errors), 2)

    def test_checkpoint_distinguishes_skipped_from_pass(self):
        cp = {
            "schema_version": "2",
            "checkpoint_id": "rot://checkpoint/cp4",
            "parent_checkpoint_id": None,
            "project_id": "rot://project/agentic-os",
            "workstream_id": "rot://workstream/survival",
            "objective_id": "rot://objective/agentic-os/cp4",
            "agent_id": "rot://agent/chatgpt/architect",
            "session_id": "rot://session/chatgpt/unique",
            "observed_source_sha": "a" * 40,
            "event_watermark": 1,
            "projection_hash": None,
            "context_pack_hash": None,
            "authority_state": "EXECUTED",
            "completed": ["schema layer"],
            "changed_paths": [],
            "decisions": [],
            "tests": [
                {"test_id": "unit", "status": "PASS", "source_sha": "a" * 40, "run_id": "r1", "evidence_hash": None},
                {"test_id": "physical", "status": "SKIPPED", "source_sha": "a" * 40, "run_id": None, "evidence_hash": None},
            ],
            "evidence": [], "blockers": [], "risks": [], "graph_delta": [], "task_delta": [], "refactor_debt": [],
            "next_actions": ["parity"], "resume_recipe": ["verify source revision", "run tests"],
        }
        self.assertEqual(list(self.checkpoint_validator.iter_errors(cp)), [])
        cp["tests"][1]["status"] = "SUCCESS"
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))

    def test_checkpoint_rejects_self_styled_git_sha(self):
        cp = {
            "schema_version": "2", "checkpoint_id": "c", "project_id": "p", "workstream_id": "w",
            "objective_id": "o", "agent_id": "a", "session_id": "s", "observed_source_sha": "HEAD",
            "event_watermark": 0, "authority_state": "PROPOSED", "completed": [], "blockers": [],
            "next_actions": ["x"], "resume_recipe": ["y"]
        }
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))


if __name__ == "__main__":
    unittest.main()
