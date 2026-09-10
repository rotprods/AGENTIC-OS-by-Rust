from __future__ import annotations

import copy
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.survival import (
    SurvivalContractError,
    build_checkpoint,
    verify_checkpoint,
)


def _state_with_noncanonical_set_order() -> dict:
    return {
        "schema_version": "2",
        "project_id": "rot://project/agentic-os",
        "north_star": "checkpoint continuity survives worker replacement",
        "current_objective_id": "rot://objective/agentic-os/checkpoint-normalization-regression",
        "observed_source_sha": "a" * 40,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [
            "rot://workstream/agentic-os/zeta",
            "rot://workstream/agentic-os/alpha",
            "rot://workstream/agentic-os/zeta",
        ],
        "active_claims": [],
        "blockers": ["rot://blocker/zeta", "rot://blocker/alpha"],
        "verified_capabilities": ["rot://capability/zeta", "rot://capability/alpha"],
        "unverified_capabilities": [],
        "decisions": [
            "rot://decision/zeta",
            "rot://decision/alpha",
            "rot://decision/zeta",
        ],
        "latest_checkpoint_id": "rot://checkpoint/agentic-os/parent",
        "projection_hash": None,
        "next_safe_actions": ["advance deterministically"],
    }


def _build(state: dict) -> dict:
    return build_checkpoint(
        state,
        checkpoint_id="rot://checkpoint/agentic-os/checkpoint-normalization-regression",
        parent_checkpoint_id=state["latest_checkpoint_id"],
        agent_id="rot://agent/test",
        session_id="rot://session/test/checkpoint-normalization-regression",
        workstream_id="rot://workstream/agentic-os/checkpoint-test",
        completed=["locked canonical checkpoint normalization"],
        blockers=list(state["blockers"]),
        next_actions=["advance deterministically"],
        resume_recipe=["load live state", "verify latest checkpoint"],
    )


class CheckpointBuilderNormalizationV2Tests(unittest.TestCase):
    def test_builder_binds_normalized_state_not_raw_json_order(self) -> None:
        state = _state_with_noncanonical_set_order()
        checkpoint = _build(state)

        self.assertNotEqual(checkpoint["state_hash"], hash_canonical(state))
        verify_checkpoint(checkpoint, state=state)

        reordered = copy.deepcopy(state)
        reordered["active_workstreams"] = list(reversed(state["active_workstreams"]))
        reordered["blockers"] = list(reversed(state["blockers"]))
        reordered["verified_capabilities"] = list(reversed(state["verified_capabilities"]))
        reordered["decisions"] = list(reversed(state["decisions"]))
        verify_checkpoint(checkpoint, state=reordered)

    def test_resealed_raw_state_hash_checkpoint_fails_closed(self) -> None:
        state = _state_with_noncanonical_set_order()
        checkpoint = _build(state)

        forged = copy.deepcopy(checkpoint)
        forged["state_hash"] = hash_canonical(state)
        forged.pop("checkpoint_hash")
        forged["checkpoint_hash"] = hash_canonical(forged)

        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_checkpoint(forged, state=state)


if __name__ == "__main__":
    unittest.main()
