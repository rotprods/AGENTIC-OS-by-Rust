from __future__ import annotations
import unittest
from rot_ai.hardness import AUTHORITY_ORDER,BASE_SKILLS,HARDNESS_LEVELS,MAX_AUTHORITY_BY_LEVEL,SKILL_CATALOG,EvidenceRecord,HardnessError,WorkContext,compile_execution_packet,compile_hardness,compile_skill_graph,evaluate_promotion,learn_failure
from rot_ai.hardness_provenance import ProviderObservation,qualify_provider_observation
SHA="a"*40

def ctx(**overrides):
    data=dict(project_id="rot://project/agentic-os",objective_id="rot://objective/hardness-v1",repo="rotprods/AGENTIC-OS-by-Rust",ref="feat/hardness-v1-self-hosting",candidate_sha=SHA,risk_classes=("ordinary-code",)); data.update(overrides); return WorkContext(**data)

class HardnessCompilerTests(unittest.TestCase):
    def test_profiles_are_monotonic_supersets(self):
        previous=set()
        for level in HARDNESS_LEVELS:
            current=set(compile_hardness(ctx(requested_level=level)).required_skills); self.assertTrue(previous.issubset(current),level); previous=current
    def test_unknown_risk_fails_closed(self): self.assertIn("UNKNOWN_RISK:quantum-unknown",compile_hardness(ctx(risk_classes=("quantum-unknown",))).blockers)
    def test_authority_escalates_to_h4(self):
        plan=compile_hardness(ctx(touches_authority=True)); self.assertGreaterEqual(HARDNESS_LEVELS.index(plan.level),4); self.assertIn("authority",plan.required_gates)
    def test_irreversible_is_h5(self): self.assertEqual(compile_hardness(ctx(irreversible=True)).level,"H5")
    def test_global_blast_radius_is_at_least_h4(self): self.assertEqual(compile_hardness(ctx(blast_radius="global")).level,"H4")
    def test_concurrency_is_at_least_h3(self): self.assertEqual(compile_hardness(ctx(concurrent_writers_possible=True)).level,"H3")
    def test_plan_is_deterministic(self):
        c=ctx(requested_level="H5",historical_failure_families=("same-ref","stale-writer")); self.assertEqual(compile_hardness(c).plan_hash,compile_hardness(c).plan_hash)
    def test_execution_packet_is_deterministic_and_lifecycle_partitioned(self):
        c=ctx(requested_level="H5",risk_classes=("production-critical",)); left=compile_execution_packet(c); right=compile_execution_packet(c); self.assertEqual(left["packet_hash"],right["packet_hash"]); self.assertEqual(set(left["lifecycle"]),{"BEFORE","DURING","AFTER","LEARNING"}); self.assertIn("preflight",left["lifecycle"]["BEFORE"]); self.assertIn("runtime-guard",left["lifecycle"]["DURING"]); self.assertIn("promotion",left["lifecycle"]["AFTER"]); self.assertIn("retrospective",left["lifecycle"]["LEARNING"]); self.assertIn("UNVERIFIED_EVIDENCE_PROVENANCE",left["stop_conditions"])
    def test_every_compiled_skill_has_contract(self):
        plan=compile_hardness(ctx(requested_level="H5")); compiled=[s for specs in compile_skill_graph(plan).values() for s in specs]; self.assertEqual(len(compiled),len(plan.required_skills)); self.assertTrue(all(s.required_inputs and s.outputs for s in compiled))
    def test_invalid_sha_rejected(self):
        with self.assertRaisesRegex(HardnessError,"lowercase full SHA"): compile_hardness(ctx(candidate_sha="abc"))

class PromotionTests(unittest.TestCase):
    def setUp(self): self.context=ctx(requested_level="H0",risk_classes=("docs",)); self.plan=compile_hardness(self.context)
    def evidence(self,gate,*,sha=SHA,status="PASS"): return EvidenceRecord(gate,self.context.repo,self.context.ref,sha,status,f"ev:{gate}:{sha[:7]}:{status}")
    def test_missing_gate_blocks(self):
        d=evaluate_promotion(context=self.context,plan=self.plan,evidence=[],current_authority="PROPOSED",requested_authority="IMPLEMENTED"); self.assertEqual(d.decision,"NO_GO"); self.assertTrue(any(x.startswith("MISSING_EXACT_HEAD_EVIDENCE") for x in d.blockers))
    def test_stale_sha_cannot_promote(self): self.assertEqual(evaluate_promotion(context=self.context,plan=self.plan,evidence=[self.evidence(g,sha="b"*40) for g in self.plan.required_gates],current_authority="PROPOSED",requested_authority="IMPLEMENTED").decision,"NO_GO")
    def test_fail_status_cannot_promote(self):
        e=[self.evidence(g) for g in self.plan.required_gates]; e[0]=self.evidence(self.plan.required_gates[0],status="FAIL"); d=evaluate_promotion(context=self.context,plan=self.plan,evidence=e,current_authority="PROPOSED",requested_authority="IMPLEMENTED"); self.assertEqual(d.decision,"NO_GO"); self.assertTrue(any(x.startswith("GATE_NOT_PASS") for x in d.blockers))
    def test_exact_evidence_allows_bounded_promotion(self): self.assertEqual(evaluate_promotion(context=self.context,plan=self.plan,evidence=[self.evidence(g) for g in self.plan.required_gates],current_authority="PROPOSED",requested_authority="IMPLEMENTED").decision,"GO")
    def test_h0_cannot_jump_to_verified(self): self.assertIn("HARDNESS_AUTHORITY_CEILING:H0:IMPLEMENTED",evaluate_promotion(context=self.context,plan=self.plan,evidence=[self.evidence(g) for g in self.plan.required_gates],current_authority="PROPOSED",requested_authority="VERIFIED").blockers)
    def test_production_requires_h5(self): self.assertIn("HARDNESS_AUTHORITY_CEILING:H0:IMPLEMENTED",evaluate_promotion(context=self.context,plan=self.plan,evidence=[self.evidence(g) for g in self.plan.required_gates],current_authority="VERIFIED",requested_authority="PRODUCTION_AUTHORITY").blockers)
    def test_h5_plain_exact_evidence_is_rejected_as_untrusted(self):
        c=ctx(requested_level="H5",risk_classes=("production-critical",)); p=compile_hardness(c); e=[EvidenceRecord(g,c.repo,c.ref,c.candidate_sha,"PASS",f"ev:{g}") for g in p.required_gates]; d=evaluate_promotion(context=c,plan=p,evidence=e,current_authority="EMPIRICALLY_QUALIFIED",requested_authority="PRODUCTION_AUTHORITY"); self.assertEqual(d.decision,"NO_GO"); self.assertTrue(any(x.startswith("UNVERIFIED_EVIDENCE_PROVENANCE") for x in d.blockers))
    def test_h5_can_recommend_production_only_with_qualified_evidence(self):
        c=ctx(requested_level="H5",risk_classes=("production-critical",)); p=compile_hardness(c); e=[qualify_provider_observation(context=c,observation=ProviderObservation("hardness-local-verifier",g,c.repo,c.ref,c.candidate_sha,"success",f"run-{g}")) for g in p.required_gates]; d=evaluate_promotion(context=c,plan=p,evidence=e,current_authority="EMPIRICALLY_QUALIFIED",requested_authority="PRODUCTION_AUTHORITY"); self.assertEqual(d.decision,"GO")
    def test_authority_regression_is_not_a_promotion(self):
        with self.assertRaises(HardnessError) as raised: evaluate_promotion(context=self.context,plan=self.plan,evidence=[],current_authority="VERIFIED",requested_authority="IMPLEMENTED")
        self.assertEqual(raised.exception.code,"AUTHORITY_REGRESSION")

class LearningTests(unittest.TestCase):
    def test_escaped_bug_compiles_to_complete_record(self):
        r=learn_failure(bug_id="BUG-R4-REF-001",root_cause="feature branch was compared with main",broken_invariant="supersession requires same ref",regression_test="test_same_ref_supersession",failure_family="causal-ref-confusion",protocol_rule="Incident identity must include repo+ref+sha+workflow+family"); self.assertTrue(r.record_hash.startswith("sha256:")); self.assertEqual(r.failure_family,"causal-ref-confusion")
    def test_incomplete_learning_rejected(self):
        with self.assertRaises(HardnessError) as raised: learn_failure(bug_id="BUG-X",root_cause="",broken_invariant="x",regression_test="x",failure_family="x",protocol_rule="x")
        self.assertEqual(raised.exception.code,"INCOMPLETE_LEARNING_RECORD")

class RegistrySanityTests(unittest.TestCase):
    def test_every_level_adds_at_least_one_skill(self): self.assertTrue(all(BASE_SKILLS[l] for l in HARDNESS_LEVELS))
    def test_every_registered_skill_has_valid_lifecycle(self): self.assertTrue(all(s.lifecycle in {"BEFORE","DURING","AFTER","LEARNING"} for s in SKILL_CATALOG.values()))
    def test_all_profile_skills_exist_in_catalog(self): self.assertEqual({s for xs in BASE_SKILLS.values() for s in xs},set(SKILL_CATALOG))
    def test_authority_order_is_strict(self): self.assertEqual([AUTHORITY_ORDER[k] for k in ("PROPOSED","IMPLEMENTED","EXECUTED","VERIFIED","EMPIRICALLY_QUALIFIED","PRODUCTION_AUTHORITY")],sorted(set(AUTHORITY_ORDER.values())))
    def test_authority_ceilings_are_monotonic(self):
        values=[AUTHORITY_ORDER[MAX_AUTHORITY_BY_LEVEL[l]] for l in HARDNESS_LEVELS]; self.assertEqual(values,sorted(values))
if __name__=="__main__": unittest.main()
