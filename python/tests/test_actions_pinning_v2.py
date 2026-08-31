from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
SHA = re.compile(r"^[0-9a-f]{40}$")


class GitHubActionsPinningTests(unittest.TestCase):
    def test_external_actions_are_pinned_to_exact_commit_sha(self) -> None:
        violations: list[str] = []
        for path in sorted(WORKFLOWS.glob("*.yml")):
            for line_number, line in enumerate(path.read_text().splitlines(), start=1):
                match = re.match(r"^\s*-?\s*uses:\s*([^\s#]+)", line)
                if not match:
                    continue
                value = match.group(1).strip("'\"")
                if value.startswith("./"):
                    continue
                if "@" not in value:
                    violations.append(f"{path.name}:{line_number}: missing @ revision")
                    continue
                _, revision = value.rsplit("@", 1)
                if not SHA.fullmatch(revision):
                    violations.append(
                        f"{path.name}:{line_number}: external action is not pinned to 40-hex SHA: {value}"
                    )
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
