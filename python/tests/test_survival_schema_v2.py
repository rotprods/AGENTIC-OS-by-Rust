from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]


def load(name: str):
    return json.loads((ROOT / "schemas" / name).read_text())


def valid_checkpoint():
    return {
        "schema_version": "2",
        "checkpoint_id": "rot://checkpoint/cp5",
        "parent_checkpoint_id": "rot://checkpoint/cp4",
        "project_id": "rot://project/agentic-os",
        "workstream_id": "rot://workstream/survival",
        "objective_id": "rot://objective/agentic-os/cp5",
        "agent_id": "rot://agent/chatgpt/architect",
        "session_id": "rot://session/chatgpt/unique",
        "observed_source_sha": "a" * 40,
        "event_watermark": 1,
        "projection_hash": None,
        "context_pack_hash": None,
        "state_hash": "sha256:" + "2" * 64,
        "authority_state": "EXECUTED",
        "completed": ["schema layer"],
        "changed_paths": [],
        "decisions": [],
        "tests": [
            {"test_id": "unit", "status": "PASS", "source_sha": "a" * 40, "run_id": "r1", "evidence_hash": None},
            {"test_id": "physical", "status": "SKIPPED", "source_sha": "a" * 40, "run_id": None, "evidence_hash": None},
        ],
        "evidence": [],
        "blockers": [],
        "risks": [],
        "graph_delta": [],
        "task_delta": [],
        "refactor_debt": [],
        "next_actions": ["parity"],
        "resume_recipe": ["verify source revision", "run tests"],
        "checkpoint_hash": "sha256:" + "1" * 64,
    }


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
            "current_objective_id": "rot://objective/agentic-os/cp5",
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
            "unverified_capabilities": [], "next_safe_actions": ["x"], "extra_field": True,
        }
        self.assertGreaterEqual(len(list(self.state_validator.iter_errors(state))), 2)

    def test_checkpoint_distinguishes_skipped_from_pass(self):
        cp = valid_checkpoint()
        self.assertEqual(list(self.checkpoint_validator.iter_errors(cp)), [])
        cp["tests"][1]["status"] = "SUCCESS"
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))

    def test_checkpoint_requires_integrity_and_state_hashes(self):
        for field in ("checkpoint_hash", "state_hash"):
            cp = valid_checkpoint()
            cp.pop(field)
            self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))
        cp = valid_checkpoint()
        cp["checkpoint_hash"] = "invalid"
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))
        cp = valid_checkpoint()
        cp["state_hash"] = "invalid"
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))

    def test_checkpoint_rejects_non_sha_observed_revision(self):
        cp = valid_checkpoint()
        cp["observed_source_sha"] = "HEAD"
        self.assertTrue(list(self.checkpoint_validator.iter_errors(cp)))


if __name__ == "__main__":
    unittest.main()
