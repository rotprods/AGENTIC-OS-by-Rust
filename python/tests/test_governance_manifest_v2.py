from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from rot_contracts.governance_manifest import (
    assert_external_governance_ready,
    validate_external_authority_manifest,
)
from rot_contracts.survival import SurvivalContractError


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "governance" / "external-authorities.v1.json"


class GovernanceManifestV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_is_structurally_valid(self):
        validate_external_authority_manifest(self.manifest)

    def test_current_manifest_fails_closed_because_cp_authorities_are_unresolved(self):
        observed = {
            "rot.knowledge": "621550ddf725c0c3d1e41540ee878be124dfe871",
            "COS2": "3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83",
        }
        with self.assertRaisesRegex(SurvivalContractError, "CP01.*unresolved"):
            assert_external_governance_ready(self.manifest, observed_heads=observed)

    def test_unresolved_entry_cannot_carry_guessed_locator(self):
        manifest = copy.deepcopy(self.manifest)
        cp01 = next(item for item in manifest["authorities"] if item["authority_id"] == "CP01")
        cp01["repository_full_name"] = "rotprods/guessed-cp01"
        with self.assertRaisesRegex(SurvivalContractError, "must not carry guessed"):
            validate_external_authority_manifest(manifest)

    def test_drift_is_rejected_once_all_required_authorities_are_pinned(self):
        manifest = copy.deepcopy(self.manifest)
        for index, authority_id in enumerate(("CP01", "CP02", "CP03"), start=1):
            item = next(entry for entry in manifest["authorities"] if entry["authority_id"] == authority_id)
            item.update({
                "source_type": "github_repository",
                "repository_full_name": f"rotprods/{authority_id.lower()}",
                "ref": "main",
                "pinned_sha": str(index) * 40,
                "content_path": None,
                "resolution_status": "PINNED",
            })
        observed = {
            "rot.knowledge": "621550ddf725c0c3d1e41540ee878be124dfe871",
            "CP01": "1" * 40,
            "CP02": "2" * 40,
            "CP03": "3" * 40,
            "COS2": "b" * 40,
        }
        with self.assertRaisesRegex(SurvivalContractError, "COS2 drift detected"):
            assert_external_governance_ready(manifest, observed_heads=observed)

    def test_complete_exact_observation_passes_when_all_authorities_are_pinned(self):
        manifest = copy.deepcopy(self.manifest)
        observed = {
            "rot.knowledge": "621550ddf725c0c3d1e41540ee878be124dfe871",
            "COS2": "3ae197ebe6024b68ea2cc33a4c54c76fbc8d1e83",
        }
        for index, authority_id in enumerate(("CP01", "CP02", "CP03"), start=1):
            sha = str(index) * 40
            item = next(entry for entry in manifest["authorities"] if entry["authority_id"] == authority_id)
            item.update({
                "source_type": "github_repository",
                "repository_full_name": f"rotprods/{authority_id.lower()}",
                "ref": "main",
                "pinned_sha": sha,
                "content_path": None,
                "resolution_status": "PINNED",
            })
            observed[authority_id] = sha
        assert_external_governance_ready(manifest, observed_heads=observed)


if __name__ == "__main__":
    unittest.main()
