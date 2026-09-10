from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
USES_LINE = re.compile(r"^\s*-\s+uses:\s+([^\s]+)@([^\s#]+)")
CARGO_LOCK_SHA256 = "03b42bf650a8f52960ce8a92bc9f36848b215640ab58f4c673b09ddf5f05f370"

APPROVED_FIRST_PARTY_NODE24 = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",  # v7.0.1
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",  # v7.0.0
    "actions/setup-node": "820762786026740c76f36085b0efc47a31fe5020",  # v7.0.0
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",  # v7.0.1
}

DEPRECATED_NODE20_ACTION_PINS = {
    "11d5960a326750d5838078e36cf38b85af677262",  # checkout v4
    "a26af69be951a213d495a4c3e4e4022e16d87065",  # setup-python v5
    "49933ea5288caeca8642d1e84afbd3f7d6820020",  # setup-node v4
    "ea165f8d65b6e75b540449e92b4886f43607fa02",  # upload-artifact v4
}


class SupplyChainPolicyV2Tests(unittest.TestCase):
    def _workflow_uses(self) -> list[tuple[Path, int, str, str]]:
        uses: list[tuple[Path, int, str, str]] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            for number, line in enumerate(workflow.read_text().splitlines(), start=1):
                match = USES_LINE.match(line)
                if match:
                    target, revision = match.groups()
                    uses.append((workflow, number, target, revision))
        return uses

    def test_external_github_actions_are_commit_sha_pinned(self) -> None:
        offenders: list[str] = []
        for workflow, number, target, revision in self._workflow_uses():
            if target.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", revision):
                offenders.append(f"{workflow.relative_to(ROOT)}:{number}:{target}@{revision}")
        self.assertEqual(offenders, [], "mutable GitHub Action revisions are forbidden")

    def test_approved_first_party_javascript_actions_use_audited_node24_commits(self) -> None:
        offenders: list[str] = []
        seen: set[str] = set()
        for workflow, number, target, revision in self._workflow_uses():
            expected = APPROVED_FIRST_PARTY_NODE24.get(target)
            if expected is None:
                continue
            seen.add(target)
            if revision != expected:
                offenders.append(
                    f"{workflow.relative_to(ROOT)}:{number}:{target}@{revision} expected {expected}"
                )
        self.assertEqual(seen, set(APPROVED_FIRST_PARTY_NODE24), "audited first-party Action inventory drifted")
        self.assertEqual(offenders, [], "first-party JS Actions must use the audited Node24-native commits")

    def test_known_deprecated_node20_action_pins_cannot_reenter_workflows(self) -> None:
        offenders: list[str] = []
        for workflow, number, target, revision in self._workflow_uses():
            if revision in DEPRECATED_NODE20_ACTION_PINS:
                offenders.append(f"{workflow.relative_to(ROOT)}:{number}:{target}@{revision}")
        self.assertEqual(offenders, [], "known Node20 Action revisions are forbidden")

    def test_checkout_disables_persisted_credentials_in_every_workflow(self) -> None:
        offenders: list[str] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            text = workflow.read_text()
            checkout_count = text.count("uses: actions/checkout@")
            if checkout_count == 0:
                continue
            persisted_false_count = text.count("persist-credentials: false")
            if checkout_count != persisted_false_count:
                offenders.append(
                    f"{workflow.relative_to(ROOT)}: checkout={checkout_count} persist-credentials:false={persisted_false_count}"
                )
        self.assertEqual(offenders, [], "every checkout use must disable credential persistence")

    def test_permanent_workflows_pin_ubuntu_runner_generation(self) -> None:
        offenders: list[str] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            text = workflow.read_text()
            if "runs-on: ubuntu-latest" in text or "runs-on: ubuntu-24.04" not in text:
                offenders.append(str(workflow.relative_to(ROOT)))
        self.assertEqual(offenders, [], "permanent workflows must pin the Ubuntu 24.04 runner generation")

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
        self.assertIn("toolchain: 1.88.0", text)
        self.assertIn("cargo metadata --locked", text)
        self.assertIn("cargo clippy --workspace --all-targets --all-features --locked", text)
        self.assertIn("cargo test --workspace --all-targets --all-features --locked", text)
        self.assertIn("cmp /tmp/Cargo.lock.before Cargo.lock", text)
        self.assertTrue((ROOT / "Cargo.lock").is_file())

    def test_python_continuity_ci_matches_hash_lock_provenance(self) -> None:
        workflow = (WORKFLOWS / "survival-v2-ci.yml").read_text()
        requirements = (ROOT / "requirements" / "continuity.txt").read_text()
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertIn("PYTHON_VERSION: '3.12.3'", workflow)
        self.assertIn(f"actions/setup-python@{APPROVED_FIRST_PARTY_NODE24['actions/setup-python']}", workflow)
        self.assertIn("python -m venv /tmp/survival-v2-venv", workflow)
        self.assertIn("--require-hashes", workflow)
        self.assertIn("--only-binary=:all:", workflow)
        self.assertIn("requirements/continuity.txt", workflow)
        self.assertNotIn("jsonschema==4.25.1", workflow)
        self.assertIn("Python 3.12.3 / ubuntu-24.04", requirements)
        package_lines = [line for line in requirements.splitlines() if line and not line.startswith(("#", " "))]
        self.assertGreaterEqual(len(package_lines), 6)
        self.assertEqual(requirements.count("--hash=sha256:"), 6)

    def test_cross_language_parity_pins_python_node_pnpm_and_hash_locked_python_closure(self) -> None:
        workflow = (WORKFLOWS / "f1-parity-ci.yml").read_text()
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertIn("PYTHON_VERSION: '3.13.15'", workflow)
        self.assertIn("NODE_VERSION: '24.20.0'", workflow)
        self.assertIn("PNPM_VERSION: '10.15.0'", workflow)
        self.assertIn(f"actions/setup-python@{APPROVED_FIRST_PARTY_NODE24['actions/setup-python']}", workflow)
        self.assertIn(f"actions/setup-node@{APPROVED_FIRST_PARTY_NODE24['actions/setup-node']}", workflow)
        self.assertIn("--require-hashes -r requirements/ci.lock", workflow)
        self.assertIn('corepack prepare "pnpm@$PNPM_VERSION" --activate', workflow)
        self.assertIn("pnpm install --frozen-lockfile", workflow)
        self.assertIn("cmp pnpm-lock.yaml /tmp/pnpm-lock.before", workflow)
        self.assertNotIn("pip install --disable-pip-version-check jsonschema==4.25.1", workflow)


if __name__ == "__main__":
    unittest.main()
