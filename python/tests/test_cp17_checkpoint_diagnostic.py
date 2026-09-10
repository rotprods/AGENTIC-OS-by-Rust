from __future__ import annotations

import json
import unittest
from pathlib import Path

from rot_contracts.survival import verify_checkpoint


ROOT = Path(__file__).resolve().parents[2]


class CP17CheckpointDiagnosticTests(unittest.TestCase):
    def test_failed_cp17_checkpoint_directly_binds_post_pointer_state(self) -> None:
        """Diagnostic: prove which durable state image CP17 actually sealed.

        The repository-level latest-checkpoint contract intentionally rewinds the
        pointer to the parent before verification.  This test checks the competing
        hypothesis: CP17 was accidentally built from the already-advanced pointer
        state.  It is temporary diagnostic evidence for the CP17 repair wave and
        must not be used to make the broken checkpoint authoritative.
        """
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        checkpoint = json.loads(
            (ROOT / "state" / "checkpoints" / "cp17-node24-actions-provenance-20260910.json").read_text()
        )
        self.assertEqual(state["latest_checkpoint_id"], checkpoint["checkpoint_id"])
        verify_checkpoint(checkpoint, state=state)


if __name__ == "__main__":
    unittest.main()
