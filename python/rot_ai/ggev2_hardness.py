from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Iterable

from .hardness import EvidenceRecord, HardnessPlan, PromotionDecision, WorkContext


def compile_hardness_projection(
    *,
    context: WorkContext,
    plan: HardnessPlan,
    promotion: PromotionDecision | None,
    evidence: Iterable[EvidenceRecord],
) -> dict[str, object]:
    evidence_rows = [asdict(item) for item in evidence]
    projection: dict[str, object] = {
        "schema_version": "1",
        "authority": "DERIVED_READ_ONLY",
        "project_id": context.project_id,
        "objective_id": context.objective_id,
        "repo": context.repo,
        "ref": context.ref,
        "candidate_sha": context.candidate_sha,
        "hardness_level": plan.level,
        "plan_hash": plan.plan_hash,
        "required_skills": list(plan.required_skills),
        "required_gates": list(plan.required_gates),
        "hardness_blockers": list(plan.blockers),
        "evidence": sorted(evidence_rows, key=lambda row: (row["gate"], row["evidence_id"])),
        "promotion": None if promotion is None else {
            "decision": promotion.decision,
            "current_authority": promotion.current_authority,
            "requested_authority": promotion.requested_authority,
            "blockers": list(promotion.blockers),
            "evidence_ids": list(promotion.evidence_ids),
        },
        "canonical_mutation_allowed": False,
        "projection_can_promote": False,
    }
    projection["projection_hash"] = _hash(projection)
    return projection


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
