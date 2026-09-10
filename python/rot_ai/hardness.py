from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Iterable

HARDNESS_LEVELS = ("H0", "H1", "H2", "H3", "H4", "H5")
LIFECYCLE = ("BEFORE", "DURING", "AFTER", "LEARNING")
AUTHORITY_ORDER = {
    "PROPOSED": 0,
    "IMPLEMENTED": 1,
    "EXECUTED": 2,
    "VERIFIED": 3,
    "EMPIRICALLY_QUALIFIED": 4,
    "PRODUCTION_AUTHORITY": 5,
}

BASE_SKILLS = {
    "H0": ("preflight", "scope", "evidence", "handoff"),
    "H1": ("runtime-guard", "unit-test", "integration-test", "refactor"),
    "H2": ("contract-test", "security-review", "regression"),
    "H3": ("concurrency", "property-test", "replay", "recovery"),
    "H4": ("authority", "fencing", "fuzz", "mutation", "security-gauntlet"),
    "H5": ("chaos", "death-drill", "supply-chain", "promotion", "retrospective"),
}

RISK_TO_MIN_LEVEL = {
    "docs": "H0",
    "ordinary-code": "H1",
    "business-critical": "H2",
    "stateful": "H3",
    "distributed": "H3",
    "security": "H4",
    "authority": "H4",
    "production-critical": "H5",
}


class HardnessError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class WorkContext:
    project_id: str
    objective_id: str
    repo: str
    ref: str
    candidate_sha: str
    risk_classes: tuple[str, ...]
    requested_level: str | None = None
    blast_radius: str = "local"
    external_inputs: bool = False
    irreversible: bool = False
    touches_secrets: bool = False
    touches_authority: bool = False
    concurrent_writers_possible: bool = False
    historical_failure_families: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceRecord:
    gate: str
    repo: str
    ref: str
    sha: str
    status: str
    evidence_id: str
    artifact_hash: str | None = None


@dataclass(frozen=True)
class HardnessPlan:
    level: str
    required_skills: tuple[str, ...]
    required_gates: tuple[str, ...]
    blockers: tuple[str, ...]
    plan_hash: str


@dataclass(frozen=True)
class PromotionDecision:
    decision: str
    current_authority: str
    requested_authority: str
    blockers: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class LearningRecord:
    bug_id: str
    root_cause: str
    broken_invariant: str
    regression_test: str
    failure_family: str
    protocol_rule: str
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        payload = {
            "bug_id": self.bug_id,
            "root_cause": self.root_cause,
            "broken_invariant": self.broken_invariant,
            "regression_test": self.regression_test,
            "failure_family": self.failure_family,
            "protocol_rule": self.protocol_rule,
        }
        object.__setattr__(self, "record_hash", _hash(payload))


def compile_hardness(context: WorkContext) -> HardnessPlan:
    _validate_context(context)
    level_index = 0
    unknown_risks: list[str] = []
    for risk in context.risk_classes:
        minimum = RISK_TO_MIN_LEVEL.get(risk)
        if minimum is None:
            unknown_risks.append(risk)
        else:
            level_index = max(level_index, HARDNESS_LEVELS.index(minimum))

    if context.requested_level is not None:
        if context.requested_level not in HARDNESS_LEVELS:
            raise HardnessError("UNKNOWN_HARDNESS_LEVEL", context.requested_level)
        level_index = max(level_index, HARDNESS_LEVELS.index(context.requested_level))

    if context.touches_authority or context.touches_secrets:
        level_index = max(level_index, HARDNESS_LEVELS.index("H4"))
    if context.irreversible:
        level_index = max(level_index, HARDNESS_LEVELS.index("H5"))
    if context.concurrent_writers_possible:
        level_index = max(level_index, HARDNESS_LEVELS.index("H3"))
    if context.blast_radius in {"cross-project", "global"}:
        level_index = max(level_index, HARDNESS_LEVELS.index("H4"))

    level = HARDNESS_LEVELS[level_index]
    skills: list[str] = []
    for idx in range(level_index + 1):
        skills.extend(BASE_SKILLS[HARDNESS_LEVELS[idx]])

    gates = _gates_for(level, context)
    blockers = tuple(f"UNKNOWN_RISK:{risk}" for risk in sorted(set(unknown_risks)))
    payload = {
        "level": level,
        "required_skills": skills,
        "required_gates": gates,
        "blockers": blockers,
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
        "historical_failure_families": sorted(context.historical_failure_families),
    }
    return HardnessPlan(level, tuple(skills), tuple(gates), blockers, _hash(payload))


def evaluate_promotion(
    *,
    context: WorkContext,
    plan: HardnessPlan,
    evidence: Iterable[EvidenceRecord],
    current_authority: str,
    requested_authority: str,
) -> PromotionDecision:
    if current_authority not in AUTHORITY_ORDER or requested_authority not in AUTHORITY_ORDER:
        raise HardnessError("UNKNOWN_AUTHORITY", "unknown authority state")
    if AUTHORITY_ORDER[requested_authority] < AUTHORITY_ORDER[current_authority]:
        raise HardnessError("AUTHORITY_REGRESSION", "promotion evaluator cannot perform rollback")

    blockers = list(plan.blockers)
    by_gate: dict[str, list[EvidenceRecord]] = {}
    accepted_ids: list[str] = []
    for item in evidence:
        by_gate.setdefault(item.gate, []).append(item)

    for gate in plan.required_gates:
        candidates = by_gate.get(gate, [])
        exact = [
            item
            for item in candidates
            if item.repo == context.repo and item.ref == context.ref and item.sha == context.candidate_sha
        ]
        if not exact:
            blockers.append(f"MISSING_EXACT_HEAD_EVIDENCE:{gate}")
            continue
        passing = [item for item in exact if item.status == "PASS"]
        if not passing:
            blockers.append(f"GATE_NOT_PASS:{gate}")
            continue
        accepted_ids.append(sorted(passing, key=lambda item: item.evidence_id)[-1].evidence_id)

    if requested_authority == "PRODUCTION_AUTHORITY" and plan.level != "H5":
        blockers.append("PRODUCTION_REQUIRES_H5")

    decision = "GO" if not blockers else "NO_GO"
    return PromotionDecision(
        decision=decision,
        current_authority=current_authority,
        requested_authority=requested_authority,
        blockers=tuple(sorted(set(blockers))),
        evidence_ids=tuple(sorted(set(accepted_ids))),
    )


def learn_failure(
    *,
    bug_id: str,
    root_cause: str,
    broken_invariant: str,
    regression_test: str,
    failure_family: str,
    protocol_rule: str,
) -> LearningRecord:
    fields = (bug_id, root_cause, broken_invariant, regression_test, failure_family, protocol_rule)
    if any(not value.strip() for value in fields):
        raise HardnessError("INCOMPLETE_LEARNING_RECORD", "all learning fields are required")
    return LearningRecord(
        bug_id=bug_id.strip(),
        root_cause=root_cause.strip(),
        broken_invariant=broken_invariant.strip(),
        regression_test=regression_test.strip(),
        failure_family=failure_family.strip(),
        protocol_rule=protocol_rule.strip(),
    )


def _gates_for(level: str, context: WorkContext) -> list[str]:
    gates = ["live-truth", "scope", "exact-head", "handoff"]
    if HARDNESS_LEVELS.index(level) >= 1:
        gates += ["unit", "integration", "refactor"]
    if HARDNESS_LEVELS.index(level) >= 2:
        gates += ["contract", "security-review", "regression"]
    if HARDNESS_LEVELS.index(level) >= 3:
        gates += ["property", "replay", "recovery", "concurrency"]
    if HARDNESS_LEVELS.index(level) >= 4:
        gates += ["fuzz", "mutation", "security-gauntlet", "authority"]
    if HARDNESS_LEVELS.index(level) >= 5:
        gates += ["chaos", "death-drill", "supply-chain", "promotion", "retrospective"]
    if context.external_inputs and "security-review" not in gates:
        gates.append("security-review")
    if context.touches_authority and "authority" not in gates:
        gates.append("authority")
    return gates


def _validate_context(context: WorkContext) -> None:
    for key, value in {
        "project_id": context.project_id,
        "objective_id": context.objective_id,
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
    }.items():
        if not value.strip():
            raise HardnessError("INVALID_CONTEXT", f"{key} is required")
    sha = context.candidate_sha
    if len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha):
        raise HardnessError("INVALID_CANDIDATE_SHA", "candidate_sha must be lowercase full SHA-1")


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
