from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.continuity_files import (
    resolve_checkpoint_id_path,
    resolve_latest_checkpoint_path,
    verify_checkpoint_lineage_topology,
    verify_latest_checkpoint_binding,
)
from rot_contracts.survival import SurvivalContractError, build_checkpoint


ROOT = Path(__file__).resolve().parents[2]
PREFIX = "rot://checkpoint/agentic-os/"


def _reseal(checkpoint: dict) -> dict:
    result = copy.deepcopy(checkpoint)
    result.pop("checkpoint_hash", None)
    result["checkpoint_hash"] = hash_canonical(result)
    return result


def _seed_state(*, latest_checkpoint_id: str | None = None) -> dict:
    return {
        "schema_version": "2",
        "project_id": "rot://project/agentic-os",
        "north_star": "checkpoint continuity survives worker replacement",
        "current_objective_id": "rot://objective/agentic-os/checkpoint-test",
        "observed_source_sha": "a" * 40,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": ["rot://workstream/agentic-os/checkpoint-test"],
        "active_claims": [],
        "blockers": ["rot://blocker/fixture"],
        "verified_capabilities": ["rot://capability/fixture"],
        "unverified_capabilities": [],
        "decisions": ["rot://decision/fixture"],
        "latest_checkpoint_id": latest_checkpoint_id,
        "projection_hash": None,
        "next_safe_actions": ["advance deterministically"],
    }


def _build_next(state: dict, slug: str) -> tuple[dict, dict]:
    checkpoint_id = PREFIX + slug
    checkpoint = build_checkpoint(
        state,
        checkpoint_id=checkpoint_id,
        agent_id="rot://agent/test",
        session_id=f"rot://session/test/{slug}",
        workstream_id="rot://workstream/agentic-os/checkpoint-test",
        completed=[f"built {slug}"],
        blockers=list(state["blockers"]),
        next_actions=["advance deterministically"],
        resume_recipe=["load live state", "resolve latest checkpoint dynamically"],
        parent_checkpoint_id=state["latest_checkpoint_id"],
    )
    advanced = copy.deepcopy(state)
    advanced["latest_checkpoint_id"] = checkpoint_id
    return advanced, checkpoint


def _write_checkpoint(root: Path, checkpoint: dict, *, filename: str | None = None) -> Path:
    directory = root / "state" / "checkpoints"
    directory.mkdir(parents=True, exist_ok=True)
    if filename is None:
        path = resolve_checkpoint_id_path(root, checkpoint["checkpoint_id"], require_exists=False)
    else:
        path = directory / filename
    path.write_text(json.dumps(checkpoint, sort_keys=True))
    return path


class LatestCheckpointBindingTests(unittest.TestCase):
    def _repository_state_checkpoint(self) -> tuple[dict, dict]:
        state = json.loads((ROOT / "state" / "project_state.json").read_text())
        checkpoint = json.loads(resolve_latest_checkpoint_path(ROOT, state).read_text())
        return state, checkpoint

    def test_repository_latest_checkpoint_exists_matches_id_and_binds_to_pre_advance_state(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        verify_latest_checkpoint_binding(state, checkpoint)

    def test_repository_checkpoint_lineage_is_structurally_unambiguous(self) -> None:
        state, _ = self._repository_state_checkpoint()
        lineage = verify_checkpoint_lineage_topology(ROOT, state)
        self.assertEqual(lineage[0], state["latest_checkpoint_id"])
        self.assertGreaterEqual(len(lineage), 1)

    def test_sequential_checkpoint_pointer_transitions_remain_deterministic(self) -> None:
        state0 = _seed_state()
        state1, cp1 = _build_next(state0, "cp-a")
        verify_latest_checkpoint_binding(state1, cp1)
        state2, cp2 = _build_next(state1, "cp-b")
        verify_latest_checkpoint_binding(state2, cp2)
        self.assertEqual(cp1["parent_checkpoint_id"], None)
        self.assertEqual(cp2["parent_checkpoint_id"], cp1["checkpoint_id"])
        self.assertEqual(state2["latest_checkpoint_id"], cp2["checkpoint_id"])

    def test_all_bound_state_fields_fail_closed_on_drift(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        mutations = {
            "blockers": lambda value: value + ["rot://blocker/tampered"],
            "authority_state": lambda _value: "VERIFIED",
            "event_watermark": lambda value: value + 1,
            "verified_capabilities": lambda value: value + ["rot://capability/tampered"],
            "observed_source_sha": lambda _value: "f" * 40,
            "active_claims": lambda value: value + ["rot://claim/tampered"],
            "active_workstreams": lambda value: value + ["rot://workstream/tampered"],
            "next_safe_actions": lambda value: value + ["tampered action"],
        }
        for field, mutate in mutations.items():
            with self.subTest(field=field):
                drifted = copy.deepcopy(state)
                drifted[field] = mutate(copy.deepcopy(state[field]))
                with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
                    verify_latest_checkpoint_binding(drifted, checkpoint)

    def test_checkpoint_identity_mismatch_fails_closed(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        checkpoint["checkpoint_id"] = PREFIX + "other"
        with self.assertRaisesRegex(SurvivalContractError, "identity mismatch"):
            verify_latest_checkpoint_binding(state, checkpoint)

    def test_tampered_parent_pointer_fails_checkpoint_integrity(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        checkpoint["parent_checkpoint_id"] = PREFIX + "tampered-parent"
        with self.assertRaisesRegex(SurvivalContractError, "integrity mismatch"):
            verify_latest_checkpoint_binding(state, checkpoint)

    def test_wrong_parent_fails_state_binding_even_if_attacker_reseals_document(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        checkpoint["parent_checkpoint_id"] = PREFIX + "cp13-assurance-operator-20260901"
        checkpoint = _reseal(checkpoint)
        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_latest_checkpoint_binding(state, checkpoint)

    def test_checkpoint_payload_tamper_fails_document_hash(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        checkpoint["completed"] = list(checkpoint["completed"]) + ["forged completion"]
        with self.assertRaisesRegex(SurvivalContractError, "integrity mismatch"):
            verify_latest_checkpoint_binding(state, checkpoint)

    def test_state_hash_tamper_fails_binding_even_when_document_is_resealed(self) -> None:
        state, checkpoint = self._repository_state_checkpoint()
        checkpoint["state_hash"] = "sha256:" + "0" * 64
        checkpoint = _reseal(checkpoint)
        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_latest_checkpoint_binding(state, checkpoint)

    def test_pointer_rollback_without_matching_historical_state_fails(self) -> None:
        state, _ = self._repository_state_checkpoint()
        rolled_back = copy.deepcopy(state)
        rolled_back["latest_checkpoint_id"] = PREFIX + "cp14-promotion-readiness-20260901"
        checkpoint = json.loads(resolve_latest_checkpoint_path(ROOT, rolled_back).read_text())
        with self.assertRaisesRegex(SurvivalContractError, "state binding mismatch"):
            verify_latest_checkpoint_binding(rolled_back, checkpoint)

    def test_missing_checkpoint_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state" / "checkpoints").mkdir(parents=True)
            state = {"latest_checkpoint_id": PREFIX + "missing"}
            with self.assertRaisesRegex(SurvivalContractError, "does not exist"):
                resolve_latest_checkpoint_path(root, state)

    def test_malformed_or_escaping_checkpoint_uri_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state" / "checkpoints").mkdir(parents=True)
            for bad in (
                PREFIX + "../escape",
                PREFIX + "a/b",
                "rot://checkpoint/other/cp10",
                "cp10",
                PREFIX,
                PREFIX + "UPPERCASE",
                PREFIX + "space here",
            ):
                with self.subTest(bad=bad):
                    with self.assertRaises(SurvivalContractError):
                        resolve_latest_checkpoint_path(root, {"latest_checkpoint_id": bad})

    def test_self_parent_checkpoint_is_detected_as_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            cp1["parent_checkpoint_id"] = cp1["checkpoint_id"]
            _write_checkpoint(root, cp1)
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state1)
            self.assertEqual(caught.exception.code, "CHECKPOINT_PARENT_CYCLE")

    def test_parent_cycle_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            state2, cp2 = _build_next(state1, "cp-b")
            cp1["parent_checkpoint_id"] = cp2["checkpoint_id"]
            _write_checkpoint(root, cp1)
            _write_checkpoint(root, cp2)
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state2)
            self.assertEqual(caught.exception.code, "CHECKPOINT_PARENT_CYCLE")

    def test_orphan_parent_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state(latest_checkpoint_id=PREFIX + "missing-parent")
            state1, cp1 = _build_next(state0, "cp-child")
            _write_checkpoint(root, cp1)
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state1)
            self.assertEqual(caught.exception.code, "CHECKPOINT_ORPHAN_PARENT")

    def test_concurrent_sibling_checkpoints_are_detected_as_fork(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            state2, cp2 = _build_next(state1, "cp-b")
            _state3, cp3 = _build_next(state1, "cp-c")
            _write_checkpoint(root, cp1)
            _write_checkpoint(root, cp2)
            _write_checkpoint(root, cp3)
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state2)
            self.assertEqual(caught.exception.code, "CHECKPOINT_LINEAGE_FORK")

    def test_checkpoint_exists_but_pointer_not_advanced_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            _state2, cp2 = _build_next(state1, "cp-b")
            _write_checkpoint(root, cp1)
            _write_checkpoint(root, cp2)
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state1)
            self.assertEqual(caught.exception.code, "CHECKPOINT_POINTER_BEHIND")

    def test_pointer_advanced_but_checkpoint_absent_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state" / "checkpoints").mkdir(parents=True)
            state = _seed_state(latest_checkpoint_id=PREFIX + "absent")
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state)
            self.assertEqual(caught.exception.code, "CHECKPOINT_NOT_FOUND")

    def test_same_checkpoint_id_under_second_filename_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            _write_checkpoint(root, cp1)
            _write_checkpoint(root, copy.deepcopy(cp1), filename="zz-duplicate.json")
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state1)
            self.assertIn(caught.exception.code, {"DUPLICATE_CHECKPOINT_ID", "CHECKPOINT_FILENAME_MISMATCH"})

    def test_checkpoint_filename_must_be_derived_from_canonical_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state0 = _seed_state()
            state1, cp1 = _build_next(state0, "cp-a")
            _write_checkpoint(root, cp1, filename="alias.json")
            with self.assertRaises(SurvivalContractError) as caught:
                verify_checkpoint_lineage_topology(root, state1)
            self.assertEqual(caught.exception.code, "CHECKPOINT_FILENAME_MISMATCH")


if __name__ == "__main__":
    unittest.main()
