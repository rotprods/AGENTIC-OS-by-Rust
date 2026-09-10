from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Iterable

from .hardness import EvidenceRecord, WorkContext, compile_execution_packet, compile_hardness


def compile_next_iteration_metaprompt(
    *,
    context: WorkContext,
    north_star: str,
    current_checkpoint: str,
    blockers: Iterable[str],
    verified_claims: Iterable[str],
    unverified_claims: Iterable[str],
    tasks: Iterable[str],
    tests: Iterable[str],
    evidence: Iterable[EvidenceRecord] = (),
) -> dict[str, object]:
    if not north_star.strip():
        raise ValueError("north_star is required")
    if not current_checkpoint.strip():
        raise ValueError("current_checkpoint is required")

    hardness = compile_hardness(context)
    execution = compile_execution_packet(context)
    evidence_rows = [asdict(item) for item in evidence]
    payload: dict[str, object] = {
        "schema_version": "1",
        "authority": "ACCELERATION_NOT_AUTHORITY",
        "directive": "VERIFY LIVE TRUTH BEFORE EXECUTION",
        "project_id": context.project_id,
        "objective_id": context.objective_id,
        "north_star": north_star.strip(),
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
        "checkpoint": current_checkpoint.strip(),
        "hardness_level": hardness.level,
        "hardness_plan_hash": hardness.plan_hash,
        "lifecycle": execution["lifecycle"],
        "required_gates": execution["required_gates"],
        "blockers": sorted(set(blockers) | set(hardness.blockers)),
        "verified_claims": sorted(set(verified_claims)),
        "unverified_claims": sorted(set(unverified_claims)),
        "tasks": list(tasks),
        "tests": list(tests),
        "evidence": sorted(evidence_rows, key=lambda row: (row["gate"], row["evidence_id"])),
        "forbidden": [
            "invent authority",
            "reuse stale exact-head evidence",
            "bypass failed required gates",
            "overwrite concurrent work",
            "treat projection as canonical truth",
        ],
        "closing_protocol": [
            "re-fetch live head",
            "run required gates",
            "persist evidence",
            "persist checkpoint/handoff",
            "compile successor packet",
        ],
    }
    payload["packet_hash"] = _hash_without_hash(payload)
    return payload


def render_metaprompt(packet: dict[str, object]) -> str:
    required = (
        "directive",
        "north_star",
        "project_id",
        "objective_id",
        "repo",
        "ref",
        "candidate_sha",
        "checkpoint",
        "hardness_level",
        "required_gates",
        "tasks",
        "tests",
        "closing_protocol",
    )
    missing = [key for key in required if key not in packet]
    if missing:
        raise ValueError(f"missing metaprompt fields: {','.join(missing)}")

    lines = [
        "/NEXT-ITERATION-METAPROMPT",
        "",
        str(packet["directive"]),
        "",
        f"North Star: {packet['north_star']}",
        f"Project: {packet['project_id']}",
        f"Objective: {packet['objective_id']}",
        f"Repo/ref/SHA: {packet['repo']} @ {packet['ref']} @ {packet['candidate_sha']}",
        f"Checkpoint: {packet['checkpoint']}",
        f"Hardness: {packet['hardness_level']}",
        "",
        "Required gates:",
    ]
    lines.extend(f"- {gate}" for gate in packet["required_gates"])
    lines.append("\nTasks:")
    lines.extend(f"- {task}" for task in packet["tasks"])
    lines.append("\nTests:")
    lines.extend(f"- {test}" for test in packet["tests"])
    lines.append("\nClosing protocol:")
    lines.extend(f"- {step}" for step in packet["closing_protocol"])
    lines.append("\nDo not claim completion without exact-head evidence and durable handoff.")
    return "\n".join(lines) + "\n"


def _hash_without_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
