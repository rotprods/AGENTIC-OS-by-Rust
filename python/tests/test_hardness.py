from __future__ import annotations

import unittest

from rot_ai.hardness import (
    AUTHORITY_ORDER,
    BASE_SKILLS,
    HARDNESS_LEVELS,
    MAX_AUTHORITY_BY_LEVEL,
    SKILL_CATALOG,
    EvidenceRecord,
    HardnessError,
    WorkContext,
    compile_execution_packet,
    compile_hardness,
    compile_skill_graph,
    evaluate_promotion,
    learn_failure,
)

SHA = "a" * 40


def ctx(**overrides):
    data = dict(
        project_id="rot://project/agentic-os",
        objective_id="rot://objective/hardness-v1",
        repo="rotprods/AGENTIC-OS-by-Rust",
        ref="feat/hardness-v1-self-hosting",
        candidate_sha=SHA,
        risk_classes=("ordinary-code",),
    )
    data.update(overrides)
    return WorkContext(**data)


class HardnessCompilerTests(unittest.TestCase):
    def test_profiles_are_monotonic_supersets(self):
        previous = set()
        for level in HARDNESS_LEVELS:
            plan = compile_hardness(ctx(requested_level=level))
            current = set(plan.required_skills)
            self.assertTrue(previous.issubset(current), level)
            previous = current

    def test_unknown_risk_fails_closed(self):
        plan = compile_hardness(ctx(risk_classes=("quantum-unknown",)))
        self.assertIn("UNKNOWN_RISK:quantum-unknown", plan.blockers)

    def test_authority_escalates_to_h4(self):
        plan = compile_hardness(ctx(touches_authority=True))
        self.assertGreaterEqual(HARDNESS_LEVELS.index(plan.level), HARDNESS_LEVELS.index("H4"))
        self.assertIn("authority", plan.required_gates)

    def test_irreversible_is_h5(self):
        self.assertEqual(compile_hardness(ctx(irreversible=True)).level, "H5")

    def test_global_blast_radius_is_at_least_h4(self):
        self.assertEqual(compile_hardness(ctx(blast_radius="global")).level, "H4")

    def test_concurrency_is_at_least_h3(self):
        self.assertEqual(compile_hardness(ctx(concurrent_writers_possible=True)).level, "H3")

    def test_plan_is_deterministic(self):
        context = ctx(requested_level="H5", historical_failure_families=("same-ref", "stale-writer"))
        self.assertEqual(compile_hardness(context).plan_hash, compile_hardness(context).plan_hash)

    def test_execution_packet_is_deterministic_and_lifecycle_partitioned(self):
        context = ctx(requested_level="H5", risk_classes=("production-critical",))
        left = compile_execution_packet(context)
        right = compile_execution_packet(context)
        self.assertEqual(left["packet_hash"], right["packet_hash"])
        self.assertEqual(set(left["lifecycle"]), {"BEFORE", "DURING", "AFTER", "LEARNING"})
        self.assertIn("preflight", left["lifecycle"]["BEFORE"])
        self.assertIn("runtime-guard", left["lifecycle"]["DURING"])
        self.assertIn("promotion", left["lifecycle"]["AFTER"])
        self.assertIn("retrospective", left["lifecycle"]["LEARNING"])

    def test_every_compiled_skill_has_contract(self):
        plan = compile_hardness(ctx(requested_level="H5"))
        graph = compile_skill_graph(plan)
        compiled = [spec for specs in graph.values() for spec in specs]
        self.assertEqual(len(compiled), len(plan.required_skills))
        self.assertTrue(all(spec.required_inputs and spec.outputs for spec in compiled))

    def test_invalid_sha_rejected(self):
        with self.assertRaisesRegex(HardnessError, "lowercase full SHA"):
            compile_hardness(ctx(candidate_sha="abc"))


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.context = ctx(requested_level="H0", risk_classes=("docs",))
        self.plan = compile_hardness(self.context)

    def evidence(self, gate, *, sha=SHA, status="PASS"):
        return EvidenceRecord(
            gate=gate,
            repo=self.context.repo,
            ref=self.context.ref,
            sha=sha,
            status=status,
            evidence_id=f"ev:{gate}:{sha[:7]}:{status}",
        )

    def test_missing_gate_blocks(self):
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=[],
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        self.assertEqual(decision.decision, "NO_GO")
        self.assertTrue(any(item.startswith("MISSING_EXACT_HEAD_EVIDENCE") for item in decision.blockers))

    def test_stale_sha_cannot_promote(self):
        evidence = [self.evidence(gate, sha="b" * 40) for gate in self.plan.required_gates]
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        self.assertEqual(decision.decision, "NO_GO")

    def test_fail_status_cannot_promote(self):
        evidence = [self.evidence(gate) for gate in self.plan.required_gates]
        evidence[0] = self.evidence(self.plan.required_gates[0], status="FAIL")
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        self.assertEqual(decision.decision, "NO_GO")
        self.assertTrue(any(item.startswith("GATE_NOT_PASS") for item in decision.blockers))

    def test_exact_evidence_allows_bounded_promotion(self):
        evidence = [self.evidence(gate) for gate in self.plan.required_gates]
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="PROPOSED",
            requested_authority="IMPLEMENTED",
        )
        self.assertEqual(decision.decision, "GO")

    def test_h0_cannot_jump_to_verified(self):
        evidence = [self.evidence(gate) for gate in self.plan.required_gates]
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="PROPOSED",
            requested_authority="VERIFIED",
        )
        self.assertEqual(decision.decision, "NO_GO")
        self.assertIn("HARDNESS_AUTHORITY_CEILING:H0:IMPLEMENTED", decision.blockers)

    def test_production_requires_h5(self):
        evidence = [self.evidence(gate) for gate in self.plan.required_gates]
        decision = evaluate_promotion(
            context=self.context,
            plan=self.plan,
            evidence=evidence,
            current_authority="VERIFIED",
            requested_authority="PRODUCTION_AUTHORITY",
        )
        self.assertEqual(decision.decision, "NO_GO")
        self.assertIn("HARDNESS_AUTHORITY_CEILING:H0:IMPLEMENTED", decision.blockers)

    def test_h5_can_recommend_production_with_all_exact_evidence(self):
        context = ctx(requested_level="H5", risk_classes=("production-critical",))
        plan = compile_hardness(context)
        evidence = [
            EvidenceRecord(gate, context.repo, context.ref, context.candidate_sha, "PASS", f"ev:{gate}")
            for gate in plan.required_gates
        ]
        decision = evaluate_promotion(
            context=context,
            plan=plan,
            evidence=evidence,
            current_authority="EMPIRICALLY_QUALIFIED",
            requested_authority="PRODUCTION_AUTHORITY",
        )
        self.assertEqual(decision.decision, "GO")

    def test_authority_regression_is_not_a_promotion(self):
        with self.assertRaises(HardnessError) as raised:
            evaluate_promotion(
                context=self.context,
                plan=self.plan,
                evidence=[],
                current_authority="VERIFIED",
                requested_authority="IMPLEMENTED",
            )
        self.assertEqual(raised.exception.code, "AUTHORITY_REGRESSION")


class LearningTests(unittest.TestCase):
    def test_escaped_bug_compiles_to_complete_record(self):
        record = learn_failure(
            bug_id="BUG-R4-REF-001",
            root_cause="feature branch was compared with main",
            broken_invariant="supersession requires same ref",
            regression_test="test_same_ref_supersession",
            failure_family="causal-ref-confusion",
            protocol_rule="Incident identity must include repo+ref+sha+workflow+family",
        )
        self.assertTrue(record.record_hash.startswith("sha256:"))
        self.assertEqual(record.failure_family, "causal-ref-confusion")

    def test_incomplete_learning_rejected(self):
        with self.assertRaises(HardnessError) as raised:
            learn_failure(
                bug_id="BUG-X",
                root_cause="",
                broken_invariant="x",
                regression_test="x",
                failure_family="x",
                protocol_rule="x",
            )
        self.assertEqual(raised.exception.code, "INCOMPLETE_LEARNING_RECORD")


class RegistrySanityTests(unittest.TestCase):
    def test_every_level_adds_at_least_one_skill(self):
        self.assertTrue(all(BASE_SKILLS[level] for level in HARDNESS_LEVELS))

    def test_every_registered_skill_has_valid_lifecycle(self):
        self.assertTrue(all(spec.lifecycle in {"BEFORE", "DURING", "AFTER", "LEARNING"} for spec in SKILL_CATALOG.values()))

    def test_all_profile_skills_exist_in_catalog(self):
        profile_skills = {skill for skills in BASE_SKILLS.values() for skill in skills}
        self.assertEqual(profile_skills, set(SKILL_CATALOG))

    def test_authority_order_is_strict(self):
        values = [AUTHORITY_ORDER[key] for key in ("PROPOSED", "IMPLEMENTED", "EXECUTED", "VERIFIED", "EMPIRICALLY_QUALIFIED", "PRODUCTION_AUTHORITY")]
        self.assertEqual(values, sorted(set(values)))

    def test_authority_ceilings_are_monotonic(self):
        values = [AUTHORITY_ORDER[MAX_AUTHORITY_BY_LEVEL[level]] for level in HARDNESS_LEVELS]
        self.assertEqual(values, sorted(values))


if __name__ == "__main__":
    unittest.main()
