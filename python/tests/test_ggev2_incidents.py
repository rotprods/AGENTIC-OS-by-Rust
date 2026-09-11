from __future__ import annotations

import unittest

from rot_ai.ggev2_incidents import IncidentCorrelationError, correlate_signals

SHA_A = "a" * 40
SHA_B = "b" * 40


def signal(
    signal_id: str,
    *,
    sha: str | None = SHA_A,
    repo: str | None = "rotprods/repo",
    ref: str | None = "main",
    workflow: str = "ci",
    family: str = "tests",
):
    return {
        "signal_id": signal_id,
        "source": "gmail",
        "repo": repo,
        "ref": ref,
        "sha": sha,
        "workflow": workflow,
        "failure_family": family,
        "observed_at": "2026-09-09T21:00:00Z",
    }


class IncidentTests(unittest.TestCase):
    def test_duplicates_collapse_to_one_causal_group(self) -> None:
        output = correlate_signals(
            [signal("m1"), signal("m2")],
            current_refs={("rotprods/repo", "main"): SHA_A},
            current_ci={("rotprods/repo", "main", "ci"): "FAILURE"},
        )
        self.assertEqual(output["metrics"]["signals_seen"], 2)
        self.assertEqual(output["metrics"]["causal_groups"], 1)
        self.assertEqual(output["incidents"][0]["signal_count"], 2)
        self.assertEqual(output["incidents"][0]["classification"], "ACTIVE")

    def test_superseded_sha_is_suppressed_only_within_same_ref(self) -> None:
        output = correlate_signals(
            [signal("m1", sha=SHA_B, ref="feature/x")],
            current_refs={("rotprods/repo", "feature/x"): SHA_A},
        )
        self.assertEqual(output["metrics"]["suppressed"], 1)
        self.assertEqual(output["suppressed"][0]["reason"], "SUPERSEDED_REF_SHA")

    def test_feature_branch_current_sha_is_not_suppressed_by_main(self) -> None:
        output = correlate_signals(
            [signal("m1", sha=SHA_B, ref="feature/x")],
            current_heads={"rotprods/repo": SHA_A},
            current_refs={("rotprods/repo", "feature/x"): SHA_B},
        )
        self.assertEqual(output["metrics"]["suppressed"], 0)
        self.assertEqual(output["incidents"][0]["classification"], "ACTIVE")
        self.assertEqual(output["incidents"][0]["reason"], "CURRENT_REF_SHA_SIGNAL")

    def test_unresolved_pr_ref_is_unknown_not_compared_to_main(self) -> None:
        output = correlate_signals(
            [signal("m1", sha=SHA_B, ref="pr:unresolved")],
            current_heads={"rotprods/repo": SHA_A},
        )
        self.assertEqual(output["metrics"]["suppressed"], 0)
        self.assertEqual(output["metrics"]["unknown"], 1)
        self.assertEqual(output["incidents"][0]["reason"], "CURRENT_REF_STATE_UNRESOLVED")

    def test_current_failure_can_remain_active(self) -> None:
        output = correlate_signals(
            [signal("m1", sha=SHA_B, ref="feature/x")],
            current_refs={("rotprods/repo", "feature/x"): SHA_A},
            current_ci={("rotprods/repo", "feature/x", "ci"): "FAILURE"},
        )
        self.assertEqual(output["incidents"][0]["classification"], "ACTIVE")
        self.assertEqual(output["incidents"][0]["reason"], "CURRENT_FAILURE_CONFIRMED")

    def test_unresolved_signal_stays_unknown(self) -> None:
        output = correlate_signals([signal("m1", repo=None, sha=None)], current_heads={})
        self.assertEqual(output["unknown"][0]["classification"], "UNKNOWN")
        self.assertEqual(output["unknown"][0]["authority_class"], "UNTRUSTED_SIGNAL_INPUT")

    def test_different_failure_families_do_not_collapse(self) -> None:
        output = correlate_signals(
            [signal("m1", family="tests"), signal("m2", family="lint")],
            current_refs={("rotprods/repo", "main"): SHA_A},
        )
        self.assertEqual(output["metrics"]["causal_groups"], 2)

    def test_same_sha_workflow_different_refs_do_not_collapse(self) -> None:
        output = correlate_signals(
            [signal("m1", ref="feature/a"), signal("m2", ref="feature/b")],
            current_refs={
                ("rotprods/repo", "feature/a"): SHA_A,
                ("rotprods/repo", "feature/b"): SHA_A,
            },
        )
        self.assertEqual(output["metrics"]["causal_groups"], 2)

    def test_legacy_main_head_remains_supported(self) -> None:
        output = correlate_signals(
            [signal("m1", ref="main")], current_heads={"rotprods/repo": SHA_A}
        )
        self.assertEqual(output["incidents"][0]["classification"], "ACTIVE")

    def test_bad_signal_rejected(self) -> None:
        with self.assertRaises(IncidentCorrelationError):
            correlate_signals([{"source": "gmail"}], current_heads={})


if __name__ == "__main__":
    unittest.main()
