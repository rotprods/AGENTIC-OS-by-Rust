from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.survival import SurvivalContractError, _normalize_state, verify_checkpoint


ROOT = Path(__file__).resolve().parents[2]


class CP17CheckpointDiagnosticTests(unittest.TestCase):
    def test_failed_cp17_checkpoint_emits_normalization_delta(self) -> None:
        """Diagnostic only: identify any raw-vs-normalized state divergence.

        The checkpoint state_hash equals the durable state after rewinding only the
        checkpoint pointer, yet verify_checkpoint rejects the binding.  Emit the
        normalized semantic hash and only the names/hashes of fields changed by
        normalization so the root cause can be fixed without rewriting evidence.
        """
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        checkpoint = json.loads(
            (ROOT / "state" / "checkpoints" / "cp17-node24-actions-provenance-20260910.json").read_text()
        )
        self.assertEqual(state["latest_checkpoint_id"], checkpoint["checkpoint_id"])

        rewound = copy.deepcopy(state)
        rewound["latest_checkpoint_id"] = checkpoint["parent_checkpoint_id"]
        normalized = _normalize_state(rewound)

        print(f"CP17_CHECKPOINT_STATE_HASH={checkpoint['state_hash']}")
        print(f"CP17_REWOUND_STATE_HASH={hash_canonical(rewound)}")
        print(f"CP17_NORMALIZED_STATE_HASH={hash_canonical(normalized)}")
        print(f"CP17_RAW_KEYS={sorted(rewound)}")
        print(f"CP17_NORMALIZED_KEYS={sorted(normalized)}")
        for field in sorted(set(rewound) | set(normalized)):
            if rewound.get(field) != normalized.get(field):
                print(
                    f"CP17_NORMALIZATION_DELTA[{field}]="
                    f"raw:{hash_canonical(rewound.get(field))}:"
                    f"normalized:{hash_canonical(normalized.get(field))}"
                )

        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_checkpoint(checkpoint, state=rewound)


if __name__ == "__main__":
    unittest.main()
