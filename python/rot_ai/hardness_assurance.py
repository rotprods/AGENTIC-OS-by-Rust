from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import random
from typing import Callable, Iterable

from .hardness import HARDNESS_LEVELS, WorkContext, compile_hardness


@dataclass(frozen=True)
class MutationCase:
    mutant_id: str
    description: str
    critical: bool


@dataclass(frozen=True)
class MutationResult:
    schema_version: str
    authority: str
    repo: str
    ref: str
    candidate_sha: str
    total: int
    killed: int
    survived: tuple[str, ...]
    critical_survivors: tuple[str, ...]
    score: float
    status: str
    evidence_hash: str


@dataclass(frozen=True)
class FuzzResult:
    schema_version: str
    authority: str
    repo: str
    ref: str
    candidate_sha: str
    seed: int
    iterations: int
    failures: tuple[dict[str, object], ...]
    status: str
    evidence_hash: str


POLICY_MUTANTS: tuple[MutationCase, ...] = (
    MutationCase("M01", "unknown risk is ignored instead of blocking", True),
    MutationCase("M02", "requested lower level overrides higher risk-derived level", True),
    MutationCase("M03", "authority-touching work remains below H4", True),
    MutationCase("M04", "irreversible work remains below H5", True),
    MutationCase("M05", "global blast radius remains below H4", True),
    MutationCase("M06", "concurrent-writer work remains below H3", True),
    MutationCase("M07", "H0 is allowed to recommend VERIFIED", True),
    MutationCase("M08", "non-literal PASS is accepted as passing evidence", True),
)


def run_policy_mutation_campaign(
    *,
    context: WorkContext,
    oracle: Callable[[MutationCase], bool],
    max_mutants: int = 64,
) -> MutationResult:
    _validate_budget(max_mutants, 1, 256, "max_mutants")
    selected = POLICY_MUTANTS[:max_mutants]
    survived: list[str] = []
    critical_survivors: list[str] = []
    for mutant in selected:
        killed = bool(oracle(mutant))
        if not killed:
            survived.append(mutant.mutant_id)
            if mutant.critical:
                critical_survivors.append(mutant.mutant_id)
    total = len(selected)
    killed_count = total - len(survived)
    score = 1.0 if total == 0 else killed_count / total
    status = "PASS" if not critical_survivors else "FAIL"
    payload = {
        "schema_version": "1",
        "authority": "EVIDENCE_ONLY",
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
        "total": total,
        "killed": killed_count,
        "survived": survived,
        "critical_survivors": critical_survivors,
        "score": score,
        "status": status,
    }
    return MutationResult(
        schema_version="1",
        authority="EVIDENCE_ONLY",
        repo=context.repo,
        ref=context.ref,
        candidate_sha=context.candidate_sha,
        total=total,
        killed=killed_count,
        survived=tuple(survived),
        critical_survivors=tuple(critical_survivors),
        score=score,
        status=status,
        evidence_hash=_hash(payload),
    )


def run_deterministic_fuzz_campaign(
    *,
    context: WorkContext,
    seed: int,
    iterations: int = 1000,
) -> FuzzResult:
    _validate_budget(iterations, 1, 100_000, "iterations")
    rng = random.Random(seed)
    known_risks = (
        "docs",
        "ordinary-code",
        "business-critical",
        "stateful",
        "distributed",
        "security",
        "authority",
        "production-critical",
    )
    failures: list[dict[str, object]] = []

    for index in range(iterations):
        count = rng.randint(1, min(5, len(known_risks)))
        risks = tuple(rng.sample(known_risks, count))
        requested = rng.choice(HARDNESS_LEVELS + (None,))
        flags = {
            "touches_authority": bool(rng.getrandbits(1)),
            "touches_secrets": bool(rng.getrandbits(1)),
            "irreversible": bool(rng.getrandbits(1)),
            "concurrent_writers_possible": bool(rng.getrandbits(1)),
            "blast_radius": rng.choice(("local", "project", "cross-project", "global")),
        }
        candidate = WorkContext(
            project_id=context.project_id,
            objective_id=context.objective_id,
            repo=context.repo,
            ref=context.ref,
            candidate_sha=context.candidate_sha,
            risk_classes=risks,
            requested_level=requested,
            **flags,
        )
        plan = compile_hardness(candidate)
        baseline = compile_hardness(
            WorkContext(
                project_id=context.project_id,
                objective_id=context.objective_id,
                repo=context.repo,
                ref=context.ref,
                candidate_sha=context.candidate_sha,
                risk_classes=risks,
            )
        )
        if HARDNESS_LEVELS.index(plan.level) < HARDNESS_LEVELS.index(baseline.level):
            failures.append(
                {
                    "iteration": index,
                    "property": "MONOTONIC_RISK_LEVEL",
                    "risks": list(risks),
                    "requested_level": requested,
                    "flags": flags,
                    "observed": plan.level,
                    "baseline": baseline.level,
                }
            )
            break
        if flags["irreversible"] and plan.level != "H5":
            failures.append({"iteration": index, "property": "IRREVERSIBLE_REQUIRES_H5", "observed": plan.level})
            break
        if (flags["touches_authority"] or flags["touches_secrets"] or flags["blast_radius"] in {"cross-project", "global"}) and HARDNESS_LEVELS.index(plan.level) < HARDNESS_LEVELS.index("H4"):
            failures.append({"iteration": index, "property": "CRITICAL_BOUNDARY_REQUIRES_H4", "observed": plan.level, "flags": flags})
            break
        if flags["concurrent_writers_possible"] and HARDNESS_LEVELS.index(plan.level) < HARDNESS_LEVELS.index("H3"):
            failures.append({"iteration": index, "property": "CONCURRENCY_REQUIRES_H3", "observed": plan.level})
            break

    status = "PASS" if not failures else "FAIL"
    payload = {
        "schema_version": "1",
        "authority": "EVIDENCE_ONLY",
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
        "seed": seed,
        "iterations": iterations,
        "failures": failures,
        "status": status,
    }
    return FuzzResult(
        schema_version="1",
        authority="EVIDENCE_ONLY",
        repo=context.repo,
        ref=context.ref,
        candidate_sha=context.candidate_sha,
        seed=seed,
        iterations=iterations,
        failures=tuple(failures),
        status=status,
        evidence_hash=_hash(payload),
    )


def result_as_json(result: MutationResult | FuzzResult) -> str:
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_budget(value: int, minimum: int, maximum: int, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{field} must be integer in [{minimum},{maximum}]")


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
