from __future__ import annotations

import unittest

from rot_ai.ggev2_collectors import (
    CollectorError,
    ObservationEnvelope,
    compile_portfolio,
    normalize_github_branch,
    normalize_github_repo,
)


class GGEV2CollectorTests(unittest.TestCase):
    def test_repo_and_branch_compile_deterministically(self) -> None:
        repo = normalize_github_repo(
            {
                "repository_full_name": "rotprods/example",
                "default_branch": "main",
                "visibility": "private",
                "archived": False,
                "permissions": {"pull": True},
            },
            observed_at="2026-09-09T23:15:00+02:00",
        )
        branch = normalize_github_branch(
            {
                "name": "main",
                "commit": {
                    "sha": "a" * 40,
                    "commit": {"verification": {"verified": True, "reason": "valid"}},
                },
                "protected": True,
                "protection": {"required_status_checks": {"enforcement_level": "everyone"}},
            },
            repo="rotprods/example",
            observed_at="2026-09-09T23:15:00+02:00",
        )
        first = compile_portfolio([branch, repo])
        second = compile_portfolio([repo, branch])
        self.assertEqual(first, second)
        self.assertEqual(first["repositories"]["rotprods/example"]["head_sha"], "a" * 40)
        self.assertEqual(first["blockers"], [])

    def test_unprotected_branch_becomes_p1_blocker(self) -> None:
        branch = normalize_github_branch(
            {
                "name": "main",
                "commit": {
                    "sha": "b" * 40,
                    "commit": {"verification": {"verified": False, "reason": "unsigned"}},
                },
                "protected": False,
                "protection": {"required_status_checks": {"enforcement_level": "off"}},
            },
            repo="rotprods/example",
            observed_at="2026-09-09T23:15:00+02:00",
        )
        result = compile_portfolio([branch])
        self.assertEqual(result["blockers"][0]["category"], "BRANCH_PROTECTION_MISSING")
        self.assertEqual(result["blockers"][0]["severity"], "P1")

    def test_blocked_source_propagates_blocker(self) -> None:
        observation = ObservationEnvelope(
            source_id="drive:registry",
            source_type="drive_projection",
            observed_at="2026-09-09T23:15:00+02:00",
            source_revision="rev-1",
            freshness="BLOCKED",
            payload={},
        )
        result = compile_portfolio([observation])
        self.assertEqual(result["blockers"][0]["category"], "SOURCE_NOT_FRESH")
        self.assertEqual(result["blockers"][0]["severity"], "P1")

    def test_missing_repo_identity_fails_closed(self) -> None:
        with self.assertRaises(CollectorError):
            normalize_github_repo({"default_branch": "main"}, observed_at="2026-09-09T23:15:00+02:00")


if __name__ == "__main__":
    unittest.main()
