from __future__ import annotations

import itertools
import unittest

from rot_ai.hardness import (
    AUTHORITY_ORDER,
    HARDNESS_LEVELS,
    MAX_AUTHORITY_BY_LEVEL,
    EvidenceRecord,
    WorkContext,
    compile_hardness,
    evaluate_promotion,
)

SHA = "d" * 40
REPO = "rotprods/AGENTIC-OS-by-Rust"
REF = "feat/hardness-v1-self-hosting"


def context(**kwargs):
    base = dict(
        project_id="rot://project/agentic-os",
        objective_id="rot://objective/hardness-v1",
        repo=REPO,
        ref=REF,
        candidate_sha=SHA,
        risk_classes=("ordinary-code",),
    )
    base.update(kwargs)
    return WorkContext(**base)


class HardnessPropertyGauntlet(unittest.TestCase):
    def test_requested_level_never_reduces_risk_derived_level(self):
        risks = ("docs", "ordinary-code", "business-critical", "stateful", "security", "production-critical")
        for risk, requested in itertools.product(risks, HARDNESS_LEVELS):
            automatic = compile_hardness(context(risk_classes=(risk,))).level
            combined = compile_hardness(context(risk_classes=(risk,), requested_level=requested)).level
            self.assertGreaterEqual(HARDNESS_LEVELS.index(combined), HARDNESS_LEVELS.index(automatic), (risk, requested))

    def test_adding_risk_never_reduces_hardness(self):
        risk_pool = ("docs", "ordinary-code", "business-critical", "stateful", "security", "production-critical")
        for size in range(1, len(risk_pool)):
            for subset in itertools.combinations(risk_pool, size):
                base = compile_hardness(context(risk_classes=subset)).level
                for extra in risk_pool:
                    expanded = compile_hardness(context(risk_classes=subset + (extra,))).level
                    self.assertGreaterEqual(HARDNESS_LEVELS.index(expanded), HARDNESS_LEVELS.index(base))

    def test_authority_ceiling_never_decreases_with_hardness(self):
        ceiling_values = [AUTHORITY_ORDER[MAX_AUTHORITY_BY_LEVEL[level]] for level in HARDNESS_LEVELS]
        self.assertEqual(ceiling_values, sorted(ceiling_values))

    def test_all_single_dimension_escalators_are_monotonic(self):
        baseline = HARDNESS_LEVELS.index(compile_hardness(context()).level)
        variants = (
            context(touches_authority=True),
            context(touches_secrets=True),
            context(irreversible=True),
            context(concurrent_writers_possible=True),
            context(blast_radius="cross-project"),
            context(blast_radius="global"),
        )
        for variant in variants:
            self.assertGreaterEqual(HARDNESS_LEVELS.index(compile_hardness(variant).level), baseline)

    def test_evidence_substitution_matrix_fails_closed(self):
        ctx = context(risk_classes=("docs",), requested_level="H0")
        plan = compile_hardness(ctx)
        substitutions = (
            {"repo": "rotprods/other", "ref": REF, "sha": SHA, "status": "PASS"},
            {"repo": REPO, "ref": "other-ref", "sha": SHA, "status": "PASS"},
            {"repo": REPO, "ref": REF, "sha": "e" * 40, "status": "PASS"},
            {"repo": REPO, "ref": REF, "sha": SHA, "status": "FAIL"},
            {"repo": REPO, "ref": REF, "sha": SHA, "status": "SKIPPED"},
            {"repo": REPO, "ref": REF, "sha": SHA, "status": "CANCELLED"},
            {"repo": REPO, "ref": REF, "sha": SHA, "status": "NOT_RUN"},
        )
        for substitution in substitutions:
            evidence = [
                EvidenceRecord(
                    gate=gate,
                    repo=substitution["repo"],
                    ref=substitution["ref"],
                    sha=substitution["sha"],
                    status=substitution["status"],
                    evidence_id=f"ev:{gate}",
                )
                for gate in plan.required_gates
            ]
            decision = evaluate_promotion(
                context=ctx,
                plan=plan,
                evidence=evidence,
                current_authority="PROPOSED",
                requested_authority="IMPLEMENTED",
            )
            self.assertEqual(decision.decision, "NO_GO", substitution)

    def test_only_literal_pass_counts(self):
        ctx = context(risk_classes=("docs",), requested_level="H0")
        plan = compile_hardness(ctx)
        misleading = ("pass", "PASS ", "SUCCESS", "VERIFIED", "text contains PASS")
        for status in misleading:
            evidence = [EvidenceRecord(g, REPO, REF, SHA, status, f"ev:{g}") for g in plan.required_gates]
            decision = evaluate_promotion(
                context=ctx,
                plan=plan,
                evidence=evidence,
                current_authority="PROPOSED",
                requested_authority="IMPLEMENTED",
            )
            self.assertEqual(decision.decision, "NO_GO", status)


if __name__ == "__main__":
    unittest.main()
