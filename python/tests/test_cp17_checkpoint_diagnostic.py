from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.survival import SurvivalContractError, verify_checkpoint


ROOT = Path(__file__).resolve().parents[2]


class CP17CheckpointDiagnosticTests(unittest.TestCase):
    def test_failed_cp17_checkpoint_emits_field_fingerprints(self) -> None:
        """Diagnostic only: fingerprint the state image seen by the latest-binding verifier.

        CP17's checkpoint hash is known to bind the durable pre-pointer commit.  The
        current repository still fails after the verifier rewinds only the pointer,
        so emit per-field semantic fingerprints to identify the unexpected drift.
        This evidence must not be interpreted as authority or as permission to
        rewrite the historical checkpoint.
        """
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        checkpoint = json.loads(
            (ROOT / "state" / "checkpoints" / "cp17-node24-actions-provenance-20260910.json").read_text()
        )
        self.assertEqual(state["latest_checkpoint_id"], checkpoint["checkpoint_id"])

        rewound = copy.deepcopy(state)
        rewound["latest_checkpoint_id"] = checkpoint["parent_checkpoint_id"]
        print(f"CP17_CHECKPOINT_STATE_HASH={checkpoint['state_hash']}")
        print(f"CP17_REWOUND_STATE_HASH={hash_canonical(rewound)}")
        for field in sorted(rewound):
            print(f"CP17_FIELD_HASH[{field}]={hash_canonical(rewound[field])}")

        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_checkpoint(checkpoint, state=rewound)


if __name__ == "__main__":
    unittest.main()
