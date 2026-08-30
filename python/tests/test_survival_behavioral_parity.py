from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts.survival import FreshnessSeal, SurvivalContractError, assert_fresh, reduce_events

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "golden" / "survival-behavior-v2.json"


class SurvivalBehavioralParityTests(unittest.TestCase):
    def test_shared_behavioral_corpus(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        seed = fixture["seed"]
        for vector in fixture["cases"]:
            expected = vector["expect"]
            if expected["status"] == "REJECT":
                with self.assertRaises(SurvivalContractError, msg=vector["name"]) as raised:
                    self._execute(seed, vector)
                self.assertEqual(raised.exception.code, expected["error_code"], vector["name"])
                continue
            result = self._execute(seed, vector)
            for key, value in expected.items():
                if key != "status":
                    self.assertEqual(result[key], value, f"{vector['name']}:{key}")

    @staticmethod
    def _execute(seed: dict, vector: dict) -> dict:
        if vector["operation"] == "reduce_events":
            return reduce_events(seed, vector["events"])
        if vector["operation"] == "assert_fresh":
            assert_fresh(FreshnessSeal(**vector["local"]), FreshnessSeal(**vector["live"]))
            return {}
        raise AssertionError(f"unknown operation {vector['operation']}")


if __name__ == "__main__":
    unittest.main()
