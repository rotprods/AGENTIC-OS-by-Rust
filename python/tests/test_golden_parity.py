from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts import canonicalize, hash_canonical

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "golden" / "canonical-json.v1.json"


class GoldenParityTests(unittest.TestCase):
    def test_canonical_goldens(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        executed = 0
        for vector in fixture["vectors"]:
            if "PLACEHOLDER" in vector["expected_sha256"]:
                continue
            self.assertEqual(canonicalize(vector["value"]), vector["expected_canonical"], vector["name"])
            self.assertEqual(hash_canonical(vector["value"]), vector["expected_sha256"], vector["name"])
            executed += 1
        self.assertGreater(executed, 0)


if __name__ == "__main__":
    unittest.main()
