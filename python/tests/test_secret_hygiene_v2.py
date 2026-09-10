from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "target", ".venv", "venv", "dist", "__pycache__"}
TEXT_SUFFIXES = {
    ".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".py", ".rs", ".ts",
    ".tsx", ".js", ".mjs", ".cjs", ".txt", ".sh", ".lock",
}

# Patterns intentionally target high-confidence credential material only. They do
# not attempt to infer generic words like password/token, which would create noisy
# false positives in security documentation and tests.
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "openai-project-key": re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b"),
    "openai-legacy-key": re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "slack-token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "google-api-key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
}


def repository_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Dockerfile", "Makefile"}:
            continue
        yield path


class SecretHygieneV2Tests(unittest.TestCase):
    def test_t03_no_high_confidence_secrets_in_durable_repository_surface(self):
        findings: list[str] = []
        for path in repository_text_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for name, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    findings.append(f"{path.relative_to(ROOT)}:{name}")
        self.assertEqual(findings, [], "credential-like material found: " + ", ".join(findings))


if __name__ == "__main__":
    unittest.main()
