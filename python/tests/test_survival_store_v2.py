from __future__ import annotations

import copy
import unittest

from rot_contracts.canonical_json import hash_canonical
from rot_contracts.survival import SurvivalContractError
from rot_contracts.survival_store import AcceptedEventStore, recover_from_bundle


HEAD = "a" * 40
PROJECT = "rot://project/agentic-os"


def seed():
    return {
        "project_id": PROJECT,
        "north_star": "zero-context recovery",
        "current_objective_id": "rot://objective/agentic-os/cp6",
        "observed_source_sha": HEAD,
        "event_watermark": 0,
        "authority_state": "IMPLEMENTED",
        "active_workstreams": [],
        "active_claims": [],
        "blockers": [],
        "verified_capabilities": [],
        "unverified_capabilities": ["event-store"],
        "decisions": [],
        "latest_checkpoint_id": None,
        "projection_hash": None,
        "next_safe_actions": ["append accepted events"],
    }


def event(sequence, event_id, event_type, payload):
    return {"event_id": event_id, "sequence": sequence, "event_type": event_type, "project_id": PROJECT, "payload": payload}


class AcceptedEventStoreTests(unittest.TestCase):
    def test_duplicate_append_is_idempotent_across_calls(self):
        store = AcceptedEventStore(seed())
        e = event(1, "e1", "blocker.added", {"blocker_id": "b1"})
        first = store.append(e)
        duplicate = store.append(copy.deepcopy(e))
        self.assertFalse(first["duplicate"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(store.event_watermark, 1)
        self.assertEqual(store.state["blockers"], ["b1"])
        self.assertEqual(first["semantic_hash"], duplicate["semantic_hash"])

    def test_duplicate_identity_with_changed_payload_fails_closed(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "blocker.added", {"blocker_id": "b1"}))
        with self.assertRaisesRegex(SurvivalContractError, "same event identity"):
            store.append(event(2, "e1", "blocker.added", {"blocker_id": "b2"}))

    def test_gap_is_rejected_before_store_mutation(self):
        store = AcceptedEventStore(seed())
        with self.assertRaisesRegex(SurvivalContractError, "discontinuity"):
            store.append(event(2, "e2", "blocker.added", {"blocker_id": "b"}))
        self.assertEqual(store.event_watermark, 0)
        self.assertEqual(store.state["blockers"], [])

    def test_recovery_bundle_rebuilds_identical_state(self):
        store = AcceptedEventStore(seed())
        store.append_many([
            event(1, "e1", "workstream.started", {"workstream_id": "rot://workstream/survival"}),
            event(2, "e2", "claim.acquired", {"claim_id": "rot://claim/schemas"}),
            event(3, "e3", "blocker.added", {"blocker_id": "parity"}),
            event(4, "e4", "next_actions.set", {"next_safe_actions": ["run parity"]}),
        ])
        bundle = store.export_recovery_bundle()
        recovered = recover_from_bundle(bundle)
        self.assertEqual(recovered, store.state)
        self.assertEqual(hash_canonical(recovered), bundle["final_state_hash"])
        self.assertEqual(bundle["event_watermark"], 4)

    def test_tampered_bundle_fails_integrity(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "blocker.added", {"blocker_id": "b1"}))
        bundle = store.export_recovery_bundle()
        tampered = copy.deepcopy(bundle)
        tampered["events"][0]["payload"]["blocker_id"] = "evil"
        with self.assertRaisesRegex(SurvivalContractError, "integrity mismatch"):
            recover_from_bundle(tampered)

    def test_resealed_bundle_with_tampered_receipt_still_fails(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "blocker.added", {"blocker_id": "b1"}))
        bundle = store.export_recovery_bundle()
        tampered = copy.deepcopy(bundle)
        tampered["event_receipts"]["e1"] = "sha256:" + "0" * 64
        unsigned = copy.deepcopy(tampered)
        unsigned.pop("bundle_hash")
        tampered["bundle_hash"] = hash_canonical(unsigned)
        with self.assertRaisesRegex(SurvivalContractError, "receipt set mismatch"):
            recover_from_bundle(tampered)

    def test_resealed_bundle_with_wrong_final_state_hash_fails(self):
        store = AcceptedEventStore(seed())
        store.append(event(1, "e1", "blocker.added", {"blocker_id": "b1"}))
        bundle = store.export_recovery_bundle()
        tampered = copy.deepcopy(bundle)
        tampered["final_state_hash"] = "sha256:" + "0" * 64
        unsigned = copy.deepcopy(tampered)
        unsigned.pop("bundle_hash")
        tampered["bundle_hash"] = hash_canonical(unsigned)
        with self.assertRaisesRegex(SurvivalContractError, "state hash mismatch"):
            recover_from_bundle(tampered)

    def test_cross_project_event_never_enters_receipts(self):
        store = AcceptedEventStore(seed())
        bad = event(1, "e1", "blocker.added", {"blocker_id": "b1"})
        bad["project_id"] = "rot://project/other"
        with self.assertRaisesRegex(SurvivalContractError, "cross-project"):
            store.append(bad)
        bundle = store.export_recovery_bundle()
        self.assertEqual(bundle["events"], [])
        self.assertEqual(bundle["event_receipts"], {})


if __name__ == "__main__":
    unittest.main()
