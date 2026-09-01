from __future__ import annotations

import unittest

from rot_contracts.promotion import PromotionReadinessError, evaluate_promotion_readiness


SHA = "a" * 40
CONTEXTS = [
    "continuity",
    "rust-contract-kernel",
    "parity",
    "durable-store-properties",
    "operator-cli",
    "assurance",
]


def policy() -> dict:
    return {
        "schema_version": "1",
        "authority": "POLICY_SPECIFICATION_ONLY",
        "promotion_authority": False,
        "evaluation": "FAIL_CLOSED",
        "repository": "rotprods/AGENTIC-OS-by-Rust",
        "branch": "feat/graph-refactor-v2-survival",
        "promotion_pr": 4,
        "required_head_signature": True,
        "required_controls": {
            "pull_request": True,
            "prevent_force_push": True,
            "prevent_deletion": True,
            "required_signatures": True,
            "strict_status_checks": True,
            "enforce_admins": True,
        },
        "required_check_contexts": CONTEXTS,
    }


def successful_checks() -> list[dict]:
    return [{"name": name, "status": "completed", "conclusion": "success"} for name in CONTEXTS]


def base_snapshot() -> dict:
    return {
        "repository": "rotprods/AGENTIC-OS-by-Rust",
        "branch": "feat/graph-refactor-v2-survival",
        "default_branch": "main",
        "head_sha": SHA,
        "head_verified": True,
        "classic_protection": None,
        "classic_required_signatures": False,
        "rulesets": [],
        "check_runs": successful_checks(),
    }


class PromotionReadinessV1Tests(unittest.TestCase):
    def test_current_unprotected_unsigned_shape_is_blocked_without_discarding_green_checks(self) -> None:
        snapshot = base_snapshot()
        snapshot["head_verified"] = False
        report = evaluate_promotion_readiness(policy(), snapshot, SHA)
        self.assertFalse(report["ready"])
        self.assertEqual(report["authority"], "DERIVED_NON_AUTHORITATIVE")
        self.assertFalse(report["promotion_authority"])
        self.assertEqual(
            {item["code"] for item in report["blockers"]},
            {"HEAD_SIGNATURE_UNVERIFIED", "PROMOTION_ENFORCEMENT_MISSING"},
        )
        self.assertEqual(set(report["observations"]["successful_check_contexts"]), set(CONTEXTS))

    def test_classic_protection_can_satisfy_policy(self) -> None:
        snapshot = base_snapshot()
        snapshot["classic_required_signatures"] = True
        snapshot["classic_protection"] = {
            "required_status_checks": {"strict": True, "contexts": CONTEXTS, "checks": []},
            "required_pull_request_reviews": {"required_approving_review_count": 1},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "enforce_admins": {"enabled": True},
        }
        report = evaluate_promotion_readiness(policy(), snapshot, SHA)
        self.assertTrue(report["ready"])
        self.assertEqual(report["status"], "READY")
        self.assertEqual(report["enforcement_mode"], "classic_branch_protection")

    def test_active_exact_branch_ruleset_can_satisfy_policy(self) -> None:
        snapshot = base_snapshot()
        snapshot["rulesets"] = [{
            "id": 7,
            "target": "branch",
            "enforcement": "active",
            "bypass_actors": [],
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/feat/graph-refactor-v2-survival"],
                    "exclude": [],
                }
            },
            "rules": [
                {"type": "deletion"},
                {"type": "non_fast_forward"},
                {"type": "pull_request"},
                {"type": "required_signatures"},
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "strict_required_status_checks_policy": True,
                        "required_status_checks": [{"context": name} for name in CONTEXTS],
                    },
                },
            ],
        }]
        report = evaluate_promotion_readiness(policy(), snapshot, SHA)
        self.assertTrue(report["ready"])
        self.assertEqual(report["enforcement_mode"], "repository_ruleset")

    def test_stale_candidate_sha_is_rejected(self) -> None:
        report = evaluate_promotion_readiness(policy(), base_snapshot(), "b" * 40)
        self.assertIn("HEAD_MISMATCH", {item["code"] for item in report["blockers"]})

    def test_missing_successful_exact_head_check_is_rejected(self) -> None:
        snapshot = base_snapshot()
        snapshot["check_runs"] = successful_checks()[:-1]
        report = evaluate_promotion_readiness(policy(), snapshot, SHA)
        self.assertIn("EXACT_HEAD_CHECKS_MISSING", {item["code"] for item in report["blockers"]})

    def test_ruleset_bypass_actor_fails_admin_enforcement(self) -> None:
        snapshot = base_snapshot()
        snapshot["rulesets"] = [{
            "id": 8,
            "target": "branch",
            "enforcement": "active",
            "bypass_actors": [{"actor_type": "OrganizationAdmin"}],
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "rules": [
                {"type": "deletion"},
                {"type": "non_fast_forward"},
                {"type": "pull_request"},
                {"type": "required_signatures"},
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "strict_required_status_checks_policy": True,
                        "required_status_checks": [{"context": name} for name in CONTEXTS],
                    },
                },
            ],
        }]
        report = evaluate_promotion_readiness(policy(), snapshot, SHA)
        self.assertFalse(report["ready"])
        self.assertIn("PROMOTION_ENFORCEMENT_MISSING", {item["code"] for item in report["blockers"]})

    def test_invalid_policy_cannot_self_grant_authority(self) -> None:
        invalid = policy()
        invalid["promotion_authority"] = True
        with self.assertRaises(PromotionReadinessError):
            evaluate_promotion_readiness(invalid, base_snapshot(), SHA)


if __name__ == "__main__":
    unittest.main()
