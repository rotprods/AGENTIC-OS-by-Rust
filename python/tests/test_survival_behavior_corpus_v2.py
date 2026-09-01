from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts.survival import FreshnessSeal, SurvivalContractError, assert_fresh, reduce_events


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "golden" / "survival-behavior-v2.json"


class SurvivalBehaviorCorpusV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text())
        assert cls.fixture["authority"] == "FIXTURE_ONLY"

    def test_shared_behavioral_corpus(self):
        seed = self.fixture["seed"]
        cases = self.fixture["cases"]
        self.assertGreater(len(cases), 0)

        for vector in cases:
            with self.subTest(vector=vector["name"]):
                expected = vector["expect"]
                try:
                    if vector["operation"] == "reduce_events":
                        result = reduce_events(seed, vector["events"])
                    elif vector["operation"] == "assert_fresh":
                        local = FreshnessSeal(**vector["local"])
                        live = FreshnessSeal(**vector["live"])
                        assert_fresh(local, live)
                        result = {}
                    else:
                        self.fail(f"unknown operation {vector['operation']}")
                except SurvivalContractError as error:
                    self.assertEqual(expected["status"], "REJECT")
                    self.assertEqual(error.code, expected["error_code"])
                    continue

                self.assertEqual(expected["status"], "PASS")
                for key, value in expected.items():
                    if key == "status":
                        continue
                    self.assertEqual(result[key], value, f"{vector['name']} mismatch for {key}")

    def test_every_rejection_declares_structured_error_code(self):
        seed = self.fixture["seed"]
        for vector in self.fixture["cases"]:
            expected = vector["expect"]
            if expected["status"] != "REJECT":
                continue
            with self.subTest(vector=vector["name"]):
                with self.assertRaises(SurvivalContractError) as raised:
                    if vector["operation"] == "reduce_events":
                        reduce_events(seed, vector["events"])
                    elif vector["operation"] == "assert_fresh":
                        assert_fresh(FreshnessSeal(**vector["local"]), FreshnessSeal(**vector["live"]))
                    else:
                        self.fail(f"unknown operation {vector['operation']}")
                self.assertEqual(raised.exception.code, expected["error_code"])
                self.assertNotEqual(raised.exception.code, "SURVIVAL_CONTRACT_ERROR")


if __name__ == "__main__":
    unittest.main()
