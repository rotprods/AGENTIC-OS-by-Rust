from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


class SchemaParityTests(unittest.TestCase):
    def test_g1_schema_corpus(self) -> None:
        corpus = json.loads((ROOT / "fixtures/schema/g1-contract-corpus.v1.json").read_text(encoding="utf-8"))
        validators = {
            name: Draft202012Validator(json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")))
            for name in ("source-identity-key.v1.schema.json", "event-append-request.v1.schema.json")
        }
        for case in corpus["cases"]:
            schema_valid = validators[case["schema"]].is_valid(case["value"])
            self.assertEqual(schema_valid, case["schema_valid"], case["name"])
            semantic_valid = schema_valid and self._semantic_valid(case["schema"], case["value"])
            self.assertEqual(semantic_valid, case["semantic_valid"], case["name"])

    @staticmethod
    def _semantic_valid(schema_name: str, value: dict[str, object]) -> bool:
        if schema_name == "source-identity-key.v1.schema.json":
            return True
        if schema_name != "event-append-request.v1.schema.json":
            return False
        stream = value.get("stream")
        caller = value.get("caller")
        return (
            isinstance(stream, dict)
            and isinstance(caller, dict)
            and isinstance(stream.get("tenant_id"), str)
            and stream.get("tenant_id") == caller.get("tenant_id")
        )


if __name__ == "__main__":
    unittest.main()
