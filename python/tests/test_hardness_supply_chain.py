from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from rot_ai.hardness_supply_chain import scan_repository_supply_chain

SHA = "c" * 40


class SupplyChainTests(unittest.TestCase):
    def build_repo(self, workflow: str, *, missing_lock: str | None = None) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "ci.yml").write_text(workflow, encoding="utf-8")
        for lock in ("Cargo.lock", "pnpm-lock.yaml", "requirements/ci.lock", "requirements/audit.lock"):
            if lock == missing_lock:
                continue
            path = root / lock
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"locked:{lock}\n", encoding="utf-8")
        return root

    def scan(self, root: Path):
        return scan_repository_supply_chain(root=root, repo="rotprods/example", ref="feature", candidate_sha=SHA)

    def test_sha_pinned_action_and_locks_pass(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n")
        result = self.scan(root)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.external_actions, 1)
        self.assertEqual(len(result.lock_hashes), 4)

    def test_tag_pinned_action_fails(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: actions/checkout@v4\n")
        result = self.scan(root)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(any(f.code == "ACTION_NOT_SHA_PINNED" for f in result.findings))

    def test_missing_action_ref_fails(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: actions/checkout\n")
        result = self.scan(root)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(any(f.code == "ACTION_REF_MISSING" for f in result.findings))

    def test_local_action_does_not_require_git_sha(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: ./actions/local\n")
        self.assertEqual(self.scan(root).status, "PASS")

    def test_missing_required_lock_is_p0(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n", missing_lock="pnpm-lock.yaml")
        result = self.scan(root)
        findings = [f for f in result.findings if f.code == "REQUIRED_LOCK_MISSING"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "P0")

    def test_evidence_hash_is_deterministic(self):
        root = self.build_repo("jobs:\n  t:\n    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n")
        self.assertEqual(self.scan(root).evidence_hash, self.scan(root).evidence_hash)

    def test_wrong_candidate_identity_rejected(self):
        root = self.build_repo("jobs:\n  t:\n    steps: []\n")
        with self.assertRaises(ValueError):
            scan_repository_supply_chain(root=root, repo="rotprods/example", ref="feature", candidate_sha="short")


if __name__ == "__main__":
    unittest.main()
