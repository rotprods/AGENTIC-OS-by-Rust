from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
import re

ACTION_LINE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_LOCKS = (
    "Cargo.lock",
    "pnpm-lock.yaml",
    "requirements/ci.lock",
    "requirements/audit.lock",
)


@dataclass(frozen=True)
class SupplyChainFinding:
    code: str
    path: str
    detail: str
    severity: str


@dataclass(frozen=True)
class SupplyChainResult:
    schema_version: str
    authority: str
    repo: str
    ref: str
    candidate_sha: str
    workflow_files: int
    external_actions: int
    lock_hashes: tuple[tuple[str, str], ...]
    findings: tuple[SupplyChainFinding, ...]
    status: str
    evidence_hash: str


def scan_repository_supply_chain(
    *,
    root: Path,
    repo: str,
    ref: str,
    candidate_sha: str,
) -> SupplyChainResult:
    _validate_identity(repo, ref, candidate_sha)
    root = root.resolve()
    findings: list[SupplyChainFinding] = []
    workflow_dir = root / ".github" / "workflows"
    workflow_files = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")) if workflow_dir.is_dir() else []
    external_actions = 0

    if not workflow_files:
        findings.append(SupplyChainFinding("NO_WORKFLOWS", ".github/workflows", "no workflow files found", "P1"))

    for path in sorted(set(workflow_files)):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        for match in ACTION_LINE.finditer(text):
            target = match.group(1).strip('"\'')
            if target.startswith("./") or target.startswith("docker://"):
                continue
            external_actions += 1
            if "@" not in target:
                findings.append(SupplyChainFinding("ACTION_REF_MISSING", rel, target, "P0"))
                continue
            _, ref_value = target.rsplit("@", 1)
            if not FULL_SHA.fullmatch(ref_value):
                findings.append(SupplyChainFinding("ACTION_NOT_SHA_PINNED", rel, target, "P1"))

    lock_hashes: list[tuple[str, str]] = []
    for rel in REQUIRED_LOCKS:
        path = root / rel
        if not path.is_file():
            findings.append(SupplyChainFinding("REQUIRED_LOCK_MISSING", rel, "required lockfile absent", "P0"))
            continue
        lock_hashes.append((rel, "sha256:" + sha256(path.read_bytes()).hexdigest()))

    status = "PASS" if not findings else "FAIL"
    payload = {
        "schema_version": "1",
        "authority": "EVIDENCE_ONLY",
        "repo": repo,
        "ref": ref,
        "candidate_sha": candidate_sha,
        "workflow_files": len(set(workflow_files)),
        "external_actions": external_actions,
        "lock_hashes": sorted(lock_hashes),
        "findings": [asdict(item) for item in findings],
        "status": status,
    }
    return SupplyChainResult(
        schema_version="1",
        authority="EVIDENCE_ONLY",
        repo=repo,
        ref=ref,
        candidate_sha=candidate_sha,
        workflow_files=len(set(workflow_files)),
        external_actions=external_actions,
        lock_hashes=tuple(sorted(lock_hashes)),
        findings=tuple(findings),
        status=status,
        evidence_hash=_hash(payload),
    )


def _validate_identity(repo: str, ref: str, candidate_sha: str) -> None:
    if not repo.strip() or not ref.strip():
        raise ValueError("repo and ref are required")
    if not FULL_SHA.fullmatch(candidate_sha):
        raise ValueError("candidate_sha must be lowercase full SHA-1")


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
