from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts.survival import FreshnessSeal, SurvivalContractError, assert_fresh, reduce_events


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "golden" / "survival-behavior-v2.json"

# Transitional adapter only. Python SurvivalContractError is currently typed but does not
# expose a structured cross-runtime `code` field. This mapping lets the shared behavioral
# corpus detect semantic drift now while keeping structured error-code parity as an explicit
# follow-up contract gap rather than falsely claiming it already exists.
ERROR_CODE_BY_MESSAGE_FRAGMENT = {
    "same event identity with different semantic payload": "EVENT_ID_COLLISION",
    "event sequence discontinuity": "SEQUENCE_DISCONTINUITY",
    "cross-project event rejected": "CROSS_PROJECT",
    "unsupported event_type": "UNSUPPORTED_EVENT",
    "stale observed source revision": "STALE_SOURCE",
    "stale event watermark": "STALE_WATERMARK",
    "stale projection": "STALE_PROJECTION",
}


def rejection_code(error: SurvivalContractError) -> str:
    message = str(error)
    for fragment, code in ERROR_CODE_BY_MESSAGE_FRAGMENT.items():
        if fragment in message:
            return code
    raise AssertionError(f"unclassified SurvivalContractError: {message}")


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
                    self.assertEqual(rejection_code(error), expected["error_code"])
                    continue

                self.assertEqual(expected["status"], "PASS")
                for key, value in expected.items():
                    if key == "status":
                        continue
                    self.assertEqual(result[key], value, f"{vector['name']} mismatch for {key}")

    def test_error_code_adapter_covers_every_rejection_in_fixture(self):
        expected_codes = {
            vector["expect"]["error_code"]
            for vector in self.fixture["cases"]
            if vector["expect"]["status"] == "REJECT"
        }
        self.assertEqual(expected_codes, set(ERROR_CODE_BY_MESSAGE_FRAGMENT.values()))


if __name__ == "__main__":
    unittest.main()
