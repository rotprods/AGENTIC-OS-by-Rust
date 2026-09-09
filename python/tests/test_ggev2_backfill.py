from __future__ import annotations

import unittest

from rot_ai.ggev2_backfill import BackfillError, parse_github_failure_email, resolve_page


class BackfillTests(unittest.TestCase):
    def test_parses_run_failed_branch_as_ref_hint(self) -> None:
        parsed = parse_github_failure_email({
            "id": "m1",
            "subject": "[rotprods/swiss-OS] Run failed: repo-guard - fix/foo (417cd92)",
            "email_ts": "2026-08-28T13:17:33Z",
        })
        self.assertEqual(parsed.repo, "rotprods/swiss-OS")
        self.assertEqual(parsed.workflow, "repo-guard")
        self.assertEqual(parsed.short_sha, "417cd92")
        self.assertEqual(parsed.source_kind, "RUN")
        self.assertEqual(parsed.ref_hint, "fix/foo")
        self.assertIsNone(parsed.pr_title)

    def test_pr_run_title_is_not_misclassified_as_ref(self) -> None:
        parsed = parse_github_failure_email({
            "id": "m2",
            "subject": "[rotprods/motion-OS] PR run failed: Merge Safe - feat(x) (7d5309d)",
        })
        self.assertEqual(parsed.workflow, "Merge Safe")
        self.assertEqual(parsed.source_kind, "PR_RUN")
        self.assertIsNone(parsed.ref_hint)
        self.assertEqual(parsed.pr_title, "feat(x)")

    def test_rejects_non_failure_subject(self) -> None:
        with self.assertRaisesRegex(BackfillError, "unsupported"):
            parse_github_failure_email({"id": "m", "subject": "hello"})

    def test_old_sha_on_same_run_ref_is_suppressed(self) -> None:
        full = "417cd9261cd09a83309730f18141418c789cc5ca"
        newer = "1072d5cfb33beee3f2afcd31a59ba00c514df170"
        page = resolve_page(
            [{"id":"m1","subject":"[rotprods/swiss-OS] Run failed: repo-guard - fix/foo (417cd92)"}],
            resolve_sha=lambda repo, short: full,
            current_refs={("rotprods/swiss-OS", "fix/foo"): newer},
        )
        self.assertEqual(page["resolved_signals"], 1)
        self.assertEqual(page["resolved_refs"], 1)
        self.assertEqual(page["correlation"]["metrics"]["suppressed"], 1)
        self.assertEqual(page["correlation"]["suppressed"][0]["reason"], "SUPERSEDED_REF_SHA")

    def test_current_feature_branch_failure_is_active_even_when_main_differs(self) -> None:
        full = "a" * 40
        page = resolve_page(
            [{"id":"m1","subject":"[rotprods/repo] Run failed: CI - feature/x (aaaaaaa)"}],
            resolve_sha=lambda repo, short: full,
            current_heads={"rotprods/repo": "b" * 40},
            current_refs={("rotprods/repo", "feature/x"): full},
        )
        self.assertEqual(page["correlation"]["metrics"]["active"], 1)
        self.assertEqual(page["correlation"]["metrics"]["suppressed"], 0)

    def test_pr_run_without_ref_resolver_is_unknown_not_suppressed(self) -> None:
        full = "a" * 40
        page = resolve_page(
            [{"id":"m1","subject":"[rotprods/repo] PR run failed: CI - feature title (aaaaaaa)"}],
            resolve_sha=lambda repo, short: full,
            current_heads={"rotprods/repo": "b" * 40},
        )
        self.assertEqual(page["unresolved_refs"], 1)
        self.assertEqual(page["correlation"]["metrics"]["unknown"], 1)
        self.assertEqual(page["correlation"]["metrics"]["suppressed"], 0)

    def test_pr_run_ref_resolver_can_bind_exact_ref(self) -> None:
        full = "a" * 40
        page = resolve_page(
            [{"id":"m1","subject":"[rotprods/repo] PR run failed: CI - feature title (aaaaaaa)"}],
            resolve_sha=lambda repo, short: full,
            resolve_ref=lambda repo, sha, kind, hint, title: "feature/x",
            current_refs={("rotprods/repo", "feature/x"): full},
        )
        self.assertEqual(page["resolved_refs"], 1)
        self.assertEqual(page["correlation"]["metrics"]["active"], 1)

    def test_unresolved_sha_stays_unknown(self) -> None:
        page = resolve_page(
            [{"id":"m1","subject":"[rotprods/repo] Run failed: CI - branch (aaaaaaa)"}],
            resolve_sha=lambda repo, short: None,
            current_heads={"rotprods/repo": "b" * 40},
        )
        self.assertEqual(page["unresolved_signals"], 1)
        self.assertEqual(page["correlation"]["metrics"]["unknown"], 1)

    def test_resolver_must_return_full_sha(self) -> None:
        with self.assertRaisesRegex(BackfillError, "invalid full SHA"):
            resolve_page(
                [{"id":"m1","subject":"[rotprods/repo] Run failed: CI - branch (aaaaaaa)"}],
                resolve_sha=lambda repo, short: "abc",
            )

    def test_checkpoint_hash_deterministic(self) -> None:
        messages = [{"id":"m1","subject":"[rotprods/repo] Run failed: CI - branch (aaaaaaa)"}]
        kwargs = dict(
            resolve_sha=lambda repo, short: "a" * 40,
            current_refs={("rotprods/repo", "branch"): "b" * 40},
            next_page_token="cursor-2",
        )
        one = resolve_page(messages, **kwargs)
        two = resolve_page(messages, **kwargs)
        self.assertEqual(one["checkpoint_hash"], two["checkpoint_hash"])


if __name__ == "__main__":
    unittest.main()
