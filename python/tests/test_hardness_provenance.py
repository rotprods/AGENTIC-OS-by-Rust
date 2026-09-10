from __future__ import annotations
import unittest
from rot_ai.hardness import EvidenceRecord, WorkContext, compile_hardness, evaluate_promotion
from rot_ai.hardness_provenance import ProviderObservation, qualify_provider_observation, qualify_github_run_payload

SHA="c"*40

def context():
    return WorkContext(project_id="rot://project/agentic-os",objective_id="rot://objective/hardness-v1",repo="rotprods/AGENTIC-OS-by-Rust",ref="feat/hardness-v1-self-hosting",candidate_sha=SHA,risk_classes=("security",),requested_level="H4")

class ProvenanceTests(unittest.TestCase):
    def test_forged_plain_records_cannot_promote_h4(self):
        ctx=context(); plan=compile_hardness(ctx)
        evidence=[EvidenceRecord(g,ctx.repo,ctx.ref,ctx.candidate_sha,"PASS",f"forged:{g}") for g in plan.required_gates]
        decision=evaluate_promotion(context=ctx,plan=plan,evidence=evidence,current_authority="EXECUTED",requested_authority="VERIFIED")
        self.assertEqual(decision.decision,"NO_GO")
        self.assertTrue(any(b.startswith("UNVERIFIED_EVIDENCE_PROVENANCE") for b in decision.blockers))

    def test_verified_provider_observations_allow_bounded_h4_promotion(self):
        ctx=context(); plan=compile_hardness(ctx)
        evidence=[qualify_provider_observation(context=ctx,observation=ProviderObservation("hardness-local-verifier",g,ctx.repo,ctx.ref,ctx.candidate_sha,"success",f"run-{g}")) for g in plan.required_gates]
        decision=evaluate_promotion(context=ctx,plan=plan,evidence=evidence,current_authority="EXECUTED",requested_authority="VERIFIED")
        self.assertEqual(decision.decision,"GO")

    def test_wrong_sha_provider_observation_rejected(self):
        ctx=context()
        with self.assertRaisesRegex(ValueError,"candidate repo\\+ref\\+sha"):
            qualify_provider_observation(context=ctx,observation=ProviderObservation("github-actions","unit",ctx.repo,ctx.ref,"d"*40,"success","42"))

    def test_non_success_provider_observation_rejected(self):
        ctx=context()
        with self.assertRaises(ValueError):
            qualify_provider_observation(context=ctx,observation=ProviderObservation("github-actions","unit",ctx.repo,ctx.ref,ctx.candidate_sha,"failure","42"))

    def test_github_payload_is_bound_to_repository_branch_sha_and_run(self):
        ctx=context()
        payload={"id":123,"head_sha":ctx.candidate_sha,"head_branch":ctx.ref,"conclusion":"success","repository":{"full_name":ctx.repo}}
        qualified=qualify_github_run_payload(context=ctx,gate="unit",payload=payload)
        self.assertTrue(qualified.provenance_verified)
        self.assertEqual(qualified.provider_run_id,"123")
        self.assertTrue(qualified.observation_hash.startswith("sha256:"))

if __name__=="__main__": unittest.main()
