from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "empirical-death-drill-submission.v1.schema.json"


def valid_submission():
    return {
        "drill_id": "rot://drill/agentic-os/zero-context/001",
        "runtime_id": "rot://runtime/fresh-successor/example",
        "session_id": "rot://session/fresh-successor/example-001",
        "fresh_context_attestation": True,
        "durable_inputs": ["AGENTS.md", "state/project_state.json"],
        "forbidden_inputs": [],
        "elapsed_seconds": 42.5,
        "reconstructed_state": {
            "project_id": "rot://project/agentic-os",
            "current_objective_id": "rot://objective/agentic-os/survival-v2-cp8",
            "observed_source_sha": "a" * 40,
            "event_watermark": 0,
            "active_workstreams": [],
            "active_claims": [],
            "blockers": [],
            "verified_capabilities": [],
            "unverified_capabilities": [],
            "next_safe_actions": ["continue safely"],
        },
    }


class EmpiricalDeathDrillSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def assert_valid(self, document):
        errors = sorted(self.validator.iter_errors(document), key=lambda error: list(error.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def assert_invalid(self, document):
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_valid_submission(self):
        self.assert_valid(valid_submission())

    def test_false_fresh_context_attestation_is_invalid(self):
        document = valid_submission()
        document["fresh_context_attestation"] = False
        self.assert_invalid(document)

    def test_forbidden_input_contamination_is_invalid(self):
        document = valid_submission()
        document["forbidden_inputs"] = ["predecessor-chat-memory"]
        self.assert_invalid(document)

    def test_empty_durable_input_ledger_is_invalid(self):
        document = valid_submission()
        document["durable_inputs"] = []
        self.assert_invalid(document)

    def test_extra_fields_are_rejected(self):
        document = valid_submission()
        document["oracle_answer"] = "forbidden"
        self.assert_invalid(document)

    def test_malformed_source_sha_is_rejected(self):
        document = valid_submission()
        document["reconstructed_state"]["observed_source_sha"] = "main"
        self.assert_invalid(document)


if __name__ == "__main__":
    unittest.main()
