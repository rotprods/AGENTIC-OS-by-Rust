from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .autoprompting import compile_next_iteration_metaprompt
from .hardness import WorkContext, compile_execution_packet, compile_hardness


@dataclass(frozen=True)
class CGEV2Task:
    task_id: str
    project_id: str
    objective_id: str
    north_star: str
    checkpoint: str
    repo: str
    ref: str
    candidate_sha: str
    risk_classes: tuple[str, ...]
    blast_radius: str = "local"
    external_inputs: bool = False
    irreversible: bool = False
    touches_secrets: bool = False
    touches_authority: bool = False
    concurrent_writers_possible: bool = False
    historical_failure_families: tuple[str, ...] = ()
    tasks: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    verified_claims: tuple[str, ...] = ()
    unverified_claims: tuple[str, ...] = ()


def compile_cgev2_hardness(task: CGEV2Task, *, enforcement_mode: str = "SHADOW") -> dict[str, object]:
    if enforcement_mode not in {"SHADOW", "ENFORCE"}:
        raise ValueError("enforcement_mode must be SHADOW or ENFORCE")
    if not task.task_id.strip():
        raise ValueError("task_id is required")

    context = WorkContext(
        project_id=task.project_id,
        objective_id=task.objective_id,
        repo=task.repo,
        ref=task.ref,
        candidate_sha=task.candidate_sha,
        risk_classes=task.risk_classes,
        blast_radius=task.blast_radius,
        external_inputs=task.external_inputs,
        irreversible=task.irreversible,
        touches_secrets=task.touches_secrets,
        touches_authority=task.touches_authority,
        concurrent_writers_possible=task.concurrent_writers_possible,
        historical_failure_families=task.historical_failure_families,
    )
    plan = compile_hardness(context)
    execution = compile_execution_packet(context)
    autoprompt = compile_next_iteration_metaprompt(
        context=context,
        north_star=task.north_star,
        current_checkpoint=task.checkpoint,
        blockers=task.blockers,
        verified_claims=task.verified_claims,
        unverified_claims=task.unverified_claims,
        tasks=task.tasks,
        tests=task.tests,
    )
    result: dict[str, object] = {
        "schema_version": "1",
        "authority": "DERIVED_EXECUTION_POLICY",
        "enforcement_mode": enforcement_mode,
        "canonical_mutation_allowed": False,
        "task_id": task.task_id,
        "project_id": task.project_id,
        "objective_id": task.objective_id,
        "hardness_level": plan.level,
        "hardness_plan_hash": plan.plan_hash,
        "hardness_blockers": list(plan.blockers),
        "execution_packet": execution,
        "next_iteration_packet": autoprompt,
        "would_block": bool(plan.blockers),
        "enforced_block": enforcement_mode == "ENFORCE" and bool(plan.blockers),
    }
    result["compilation_hash"] = _hash(result)
    return result


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
