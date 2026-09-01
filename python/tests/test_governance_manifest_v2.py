from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from rot_contracts.governance_manifest import (
    assert_external_governance_locators_fresh,
    assert_external_governance_ready,
    validate_external_authority_manifest,
)
from rot_contracts.survival import SurvivalContractError


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "governance" / "external-authorities.v2.json"
LEGACY_MANIFEST_PATH = ROOT / "governance" / "external-authorities.v1.json"
GOVERNANCE_CANDIDATE_SHA = "48b0d1eddb83b165237268c4334d6e19bbd969ec"


class GovernanceManifestV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.legacy_manifest = json.loads(LEGACY_MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.observed = {
            "rot.knowledge": "6fcd62059f087c88454c555380c6eb37b7ad3ec2",
            "CP01": GOVERNANCE_CANDIDATE_SHA,
            "CP02": GOVERNANCE_CANDIDATE_SHA,
            "CP03": GOVERNANCE_CANDIDATE_SHA,
            "COS2": "3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83",
        }

    def test_legacy_v1_manifest_remains_structurally_valid(self):
        validate_external_authority_manifest(self.legacy_manifest)

    def test_current_v2_manifest_is_structurally_valid(self):
        validate_external_authority_manifest(self.manifest)

    def test_cp_candidates_are_exactly_located_but_not_promoted(self):
        expected = {
            "CP01": "life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP01_INDEPENDENT_GITHUB_QUALIFICATION_2026-09-01.md",
            "CP02": "life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP02_MID01_INDEPENDENT_DEEP_2026-09-01.md",
            "CP03": "life-os-control/subsystems/agentic-context-mesh/evidence/ACM_CP03_SQLITE_INDEPENDENT_QUALIFICATION_2026-09-01.md",
        }
        for authority_id, content_path in expected.items():
            item = next(entry for entry in self.manifest["authorities"] if entry["authority_id"] == authority_id)
            self.assertEqual(item["resolution_status"], "CANDIDATE_PINNED")
            self.assertEqual(item["repository_full_name"], "rotprods/rot.knowledge")
            self.assertEqual(item["ref"], "feat/rot-life-graph-os-foundation")
            self.assertEqual(item["pinned_sha"], GOVERNANCE_CANDIDATE_SHA)
            self.assertEqual(item["content_path"], content_path)
            self.assertTrue(item["promotion_blockers"])

    def test_candidate_locators_can_be_proven_fresh_without_granting_promotion(self):
        assert_external_governance_locators_fresh(self.manifest, observed_heads=self.observed)
        with self.assertRaisesRegex(
            SurvivalContractError,
            "CP01.*candidate-pinned.*not promotion-qualified",
        ) as error:
            assert_external_governance_ready(self.manifest, observed_heads=self.observed)
        self.assertEqual(error.exception.code, "GOVERNANCE_AUTHORITY_NOT_PROMOTION_QUALIFIED")

    def test_candidate_drift_is_rejected_even_before_promotion(self):
        observed = dict(self.observed)
        observed["CP02"] = "0" * 40
        with self.assertRaisesRegex(SurvivalContractError, "CP02 drift detected") as error:
            assert_external_governance_locators_fresh(self.manifest, observed_heads=observed)
        self.assertEqual(error.exception.code, "GOVERNANCE_AUTHORITY_DRIFT")

    def test_candidate_pin_requires_nonempty_promotion_blockers(self):
        manifest = copy.deepcopy(self.manifest)
        cp02 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP02")
        cp02["promotion_blockers"] = []
        with self.assertRaisesRegex(SurvivalContractError, "CP02 requires promotion_blockers"):
            validate_external_authority_manifest(manifest)

    def test_candidate_pin_requires_exact_locator(self):
        manifest = copy.deepcopy(self.manifest)
        cp03 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP03")
        cp03["pinned_sha"] = None
        with self.assertRaisesRegex(SurvivalContractError, "CP03 SHA invalid"):
            validate_external_authority_manifest(manifest)

    def test_content_path_must_be_repository_relative_and_non_traversing(self):
        manifest = copy.deepcopy(self.manifest)
        cp01 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP01")
        cp01["content_path"] = "../authority.md"
        with self.assertRaisesRegex(SurvivalContractError, "CP01 content_path invalid"):
            validate_external_authority_manifest(manifest)

    def test_unresolved_entry_still_cannot_carry_a_locator(self):
        manifest = copy.deepcopy(self.manifest)
        cp01 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP01")
        cp01["resolution_status"] = "UNRESOLVED"
        cp01.pop("promotion_blockers")
        with self.assertRaisesRegex(SurvivalContractError, "must not carry guessed"):
            validate_external_authority_manifest(manifest)

    def test_final_pin_cannot_retain_candidate_promotion_blockers(self):
        manifest = copy.deepcopy(self.manifest)
        cp01 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP01")
        cp01["resolution_status"] = "PINNED"
        with self.assertRaisesRegex(SurvivalContractError, "must not carry promotion_blockers"):
            validate_external_authority_manifest(manifest)

    def test_all_final_pins_with_exact_observations_are_promotion_ready(self):
        manifest = copy.deepcopy(self.manifest)
        for authority_id in ("CP01", "CP02", "CP03"):
            item = next(entry for entry in manifest["authorities"] if entry["authority_id"] == authority_id)
            item["resolution_status"] = "PINNED"
            item.pop("promotion_blockers")
        assert_external_governance_ready(manifest, observed_heads=self.observed)


if __name__ == "__main__":
    unittest.main()
