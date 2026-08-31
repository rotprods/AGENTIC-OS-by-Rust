import json
import tempfile
import unittest
from pathlib import Path

from rot_contracts.continuity_files import resolve_latest_checkpoint_path
from rot_contracts.survival import SurvivalContractError, verify_checkpoint


ROOT = Path(__file__).resolve().parents[2]


class LatestCheckpointBindingTests(unittest.TestCase):
    def test_repository_latest_checkpoint_exists_matches_id_and_binds_to_state(self) -> None:
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        checkpoint_path = resolve_latest_checkpoint_path(ROOT, state)
        checkpoint = json.loads(checkpoint_path.read_text())
        self.assertEqual(checkpoint["checkpoint_id"], state["latest_checkpoint_id"])
        verify_checkpoint(checkpoint, state=state)

    def test_missing_checkpoint_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state" / "checkpoints").mkdir(parents=True)
            state = {"latest_checkpoint_id": "rot://checkpoint/agentic-os/missing"}
            with self.assertRaisesRegex(SurvivalContractError, "does not exist"):
                resolve_latest_checkpoint_path(root, state)

    def test_path_escape_checkpoint_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state" / "checkpoints").mkdir(parents=True)
            for bad in (
                "rot://checkpoint/agentic-os/../escape",
                "rot://checkpoint/agentic-os/a/b",
                "rot://checkpoint/other/cp10",
                "cp10",
            ):
                with self.subTest(bad=bad):
                    with self.assertRaises(SurvivalContractError):
                        resolve_latest_checkpoint_path(root, {"latest_checkpoint_id": bad})


if __name__ == "__main__":
    unittest.main()
