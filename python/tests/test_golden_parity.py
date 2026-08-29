from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts import canonicalize, hash_canonical
from rot_contracts.identity_kernel import (
    derive_canonical_entity_id,
    derive_source_record_id,
    normalize_strict_source_identity,
)

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_FIXTURE = ROOT / "fixtures" / "golden" / "canonical-json.v1.json"
IDENTITY_FIXTURE = ROOT / "fixtures" / "golden" / "identity.v1.json"


class GoldenParityTests(unittest.TestCase):
    def test_canonical_goldens(self) -> None:
        fixture = json.loads(CANONICAL_FIXTURE.read_text(encoding="utf-8"))
        for vector in fixture["vectors"]:
            self.assertEqual(canonicalize(vector["value"]), vector["expected_canonical"], vector["name"])
            self.assertEqual(hash_canonical(vector["value"]), vector["expected_sha256"], vector["name"])

    def test_identity_goldens(self) -> None:
        fixture = json.loads(IDENTITY_FIXTURE.read_text(encoding="utf-8"))
        for vector in fixture["source_vectors"]:
            normalized = normalize_strict_source_identity(vector["input"])
            expected = dict(vector["expected"])
            expected_id = expected.pop("source_record_id")
            self.assertEqual(normalized, expected, vector["name"])
            self.assertEqual(derive_source_record_id(normalized), expected_id, vector["name"])
        for vector in fixture["entity_vectors"]:
            self.assertEqual(
                derive_canonical_entity_id(vector["command"]),
                vector["expected_entity_id"],
                vector["name"],
            )


if __name__ == "__main__":
    unittest.main()
