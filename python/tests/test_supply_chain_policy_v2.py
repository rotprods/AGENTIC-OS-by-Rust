from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
PINNED_ACTION = re.compile(r"^\s*-\s+uses:\s+([^\s]+)@([0-9a-f]{40})(?:\s+#.*)?$")
USES_LINE = re.compile(r"^\s*-\s+uses:\s+([^\s]+)@([^\s#]+)")
CARGO_LOCK_SHA256 = "03b42bf650a8f52960ce8a92bc9f36848b215640ab58f4c673b09ddf5f05f370"


class SupplyChainPolicyV2Tests(unittest.TestCase):
    def test_external_github_actions_are_commit_sha_pinned(self) -> None:
        offenders: list[str] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            for number, line in enumerate(workflow.read_text().splitlines(), start=1):
                match = USES_LINE.match(line)
                if not match:
                    continue
                target, revision = match.groups()
                if target.startswith("./"):
                    continue
                if not re.fullmatch(r"[0-9a-f]{40}", revision):
                    offenders.append(f"{workflow.relative_to(ROOT)}:{number}:{target}@{revision}")
        self.assertEqual(offenders, [], "mutable GitHub Action revisions are forbidden")

    def test_permanent_workflows_do_not_request_contents_write(self) -> None:
        offenders: list[str] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            text = workflow.read_text()
            if re.search(r"(?m)^\s*contents:\s*write\s*$", text):
                offenders.append(str(workflow.relative_to(ROOT)))
        self.assertEqual(offenders, [], "contents:write requires an explicit temporary exception")

    def test_rust_ci_enforces_frozen_dependency_graph(self) -> None:
        text = (WORKFLOWS / "f1-rust-ci.yml").read_text()
        self.assertIn(CARGO_LOCK_SHA256, text)
        self.assertIn("cargo metadata --locked", text)
        self.assertIn("cargo clippy --workspace --all-targets --all-features --locked", text)
        self.assertIn("cargo test --workspace --all-targets --all-features --locked", text)
        self.assertIn("cmp /tmp/Cargo.lock.before Cargo.lock", text)
        self.assertTrue((ROOT / "Cargo.lock").is_file())

    def test_python_continuity_ci_is_isolated_and_hash_locked(self) -> None:
        workflow = (WORKFLOWS / "survival-v2-ci.yml").read_text()
        requirements = (ROOT / "requirements" / "continuity.txt").read_text()
        self.assertIn("python -m venv /tmp/survival-v2-venv", workflow)
        self.assertIn("--require-hashes", workflow)
        self.assertIn("--only-binary=:all:", workflow)
        self.assertIn("requirements/continuity.txt", workflow)
        self.assertNotIn("python -m pip install --disable-pip-version-check jsonschema==4.25.1", workflow)
        package_lines = [line for line in requirements.splitlines() if line and not line.startswith(("#", " "))]
        self.assertGreaterEqual(len(package_lines), 6)
        self.assertEqual(requirements.count("--hash=sha256:"), 6)


if __name__ == "__main__":
    unittest.main()
