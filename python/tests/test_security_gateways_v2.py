from __future__ import annotations

import json
from pathlib import Path
import unittest

from rot_contracts.security_gateways import (
    MAX_EXTERNAL_CONTENT_BYTES,
    NetworkPolicy,
    ProcessPolicy,
    plan_network_request,
    plan_process_invocation,
    seal_untrusted_content,
    validate_resolved_addresses,
)
from rot_contracts.survival import SurvivalContractError


FIXTURE = Path("fixtures/security/untrusted-content-v1.json")


def assert_code(test: unittest.TestCase, expected: str, fn, *args, **kwargs) -> None:
    with test.assertRaises(SurvivalContractError) as caught:
        fn(*args, **kwargs)
    test.assertEqual(caught.exception.code, expected)


class SecurityGatewayV2Tests(unittest.TestCase):
    def test_t01_t02_adversarial_external_content_remains_non_authoritative_data(self):
        corpus = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(corpus["cases"]), 10)
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                payload = case["payload"]
                envelope = seal_untrusted_content(
                    payload,
                    source_uri=f"fixture://security/{case['id']}",
                )
                self.assertEqual(envelope.content, payload)
                self.assertEqual(envelope.trust_classification, "UNTRUSTED_DATA")
                self.assertFalse(envelope.instruction_authority)
                self.assertFalse(envelope.evidence_authority)
                self.assertFalse(envelope.promotion_authority)
                context = envelope.as_context()
                self.assertEqual(context["content"], payload)
                self.assertFalse(context["instruction_authority"])
                self.assertFalse(context["evidence_authority"])
                self.assertFalse(context["promotion_authority"])
                self.assertEqual(
                    set(context),
                    {
                        "source_uri", "content", "content_hash", "byte_length",
                        "trust_classification", "instruction_authority",
                        "evidence_authority", "promotion_authority",
                    },
                )

    def test_t01_t02_external_content_is_bounded_and_hashed(self):
        envelope = seal_untrusted_content("hello", source_uri="provider://example")
        self.assertTrue(envelope.content_hash.startswith("sha256:"))
        self.assertEqual(envelope.byte_length, 5)
        assert_code(
            self,
            "EXTERNAL_CONTENT_TOO_LARGE",
            seal_untrusted_content,
            "x" * (MAX_EXTERNAL_CONTENT_BYTES + 1),
            source_uri="provider://example",
        )

    def test_t05_https_plan_requires_explicit_trust_and_revalidation(self):
        plan = plan_network_request(
            "https://example.com/data?q=1",
            trust_classification="UNTRUSTED_EXTERNAL",
            provenance="test:t05",
        )
        self.assertEqual(plan.scheme, "https")
        self.assertEqual(plan.host, "example.com")
        self.assertTrue(plan.requires_resolution_validation)
        self.assertEqual(plan.redirect_policy, "REVALIDATE_EACH_HOP")
        self.assertFalse(plan.forward_credentials)
        self.assertEqual(validate_resolved_addresses(plan, ["8.8.8.8"]), ("8.8.8.8",))

    def test_t05_scheme_credentials_fragment_and_method_are_fail_closed(self):
        assert_code(
            self, "NETWORK_SCHEME_DENIED", plan_network_request,
            "file:///etc/passwd",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
        )
        assert_code(
            self, "NETWORK_CREDENTIALS_FORBIDDEN", plan_network_request,
            "https://user:secret@example.com/",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
        )
        assert_code(
            self, "NETWORK_FRAGMENT_FORBIDDEN", plan_network_request,
            "https://example.com/#secret",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
        )
        assert_code(
            self, "NETWORK_METHOD_DENIED", plan_network_request,
            "https://example.com/",
            method="POST", trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
        )
        assert_code(
            self, "NETWORK_TRUST_CLASSIFICATION_REQUIRED", plan_network_request,
            "https://example.com/",
            trust_classification="UNKNOWN", provenance="test",
        )

    def test_t05_local_private_link_local_and_non_global_literals_are_rejected(self):
        cases = [
            ("https://localhost/", "NETWORK_LOCALHOST_FORBIDDEN"),
            ("https://api.localhost/", "NETWORK_LOCALHOST_FORBIDDEN"),
            ("https://127.0.0.1/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://10.0.0.1/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://169.254.1.1/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://[::1]/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://[fe80::1]/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://0.0.0.0/", "NETWORK_ADDRESS_FORBIDDEN"),
            ("https://100.64.0.1/", "NETWORK_ADDRESS_FORBIDDEN"),
        ]
        for url, code in cases:
            with self.subTest(url=url):
                assert_code(
                    self, code, plan_network_request, url,
                    trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
                )

    def test_t05_dns_resolution_must_also_be_public_for_each_hop(self):
        plan = plan_network_request(
            "https://example.com/",
            trust_classification="UNTRUSTED_EXTERNAL",
            provenance="test",
        )
        for address in ("127.0.0.1", "10.0.0.1", "169.254.10.2", "::1", "fe80::1"):
            with self.subTest(address=address):
                assert_code(
                    self, "NETWORK_ADDRESS_FORBIDDEN",
                    validate_resolved_addresses, plan, [address],
                )
        assert_code(
            self, "NETWORK_RESOLUTION_EMPTY",
            validate_resolved_addresses, plan, [],
        )

    def test_t05_explicit_host_allowlist_is_exact(self):
        policy = NetworkPolicy(allowed_hosts=("api.example.com",))
        plan_network_request(
            "https://api.example.com/v1",
            trust_classification="PINNED_AUTHORITY",
            provenance="test",
            policy=policy,
        )
        assert_code(
            self, "NETWORK_HOST_NOT_ALLOWED", plan_network_request,
            "https://evil.example.com/",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test", policy=policy,
        )

    def test_t05_policy_bounds_are_enforced(self):
        assert_code(
            self, "NETWORK_POLICY_INVALID", plan_network_request,
            "https://example.com/",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
            policy=NetworkPolicy(max_redirects=999),
        )
        assert_code(
            self, "NETWORK_POLICY_INVALID", plan_network_request,
            "https://example.com/",
            trust_classification="UNTRUSTED_EXTERNAL", provenance="test",
            policy=NetworkPolicy(allowed_schemes=("file",)),
        )

    def test_t06_process_plan_is_argv_only_bounded_and_auditable(self):
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
            allowed_env_keys=("LANG",),
        )
        plan = plan_process_invocation(
            "/usr/bin/git",
            ["status", "--porcelain"],
            cwd="/workspace/repo",
            env={"LANG": "C"},
            provenance="test:t06",
            policy=policy,
        )
        self.assertFalse(plan.shell)
        self.assertTrue(plan.capture_output)
        self.assertEqual(plan.argv, ("status", "--porcelain"))
        self.assertEqual(plan.environment_keys, ("LANG",))
        self.assertEqual(plan.audit_record()["shell"], False)

    def test_t06_shell_interpreters_are_never_executable_surface(self):
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
        )
        assert_code(
            self, "PROCESS_SHELL_FORBIDDEN", plan_process_invocation,
            "/bin/sh", ["-c", "id"], cwd="/workspace",
            env={}, provenance="test", policy=policy,
        )
        assert_code(
            self, "PROCESS_POLICY_INVALID", plan_process_invocation,
            "/bin/sh", ["-c", "id"], cwd="/workspace",
            env={}, provenance="test",
            policy=ProcessPolicy(
                allowed_executables=("/bin/sh",),
                allowed_cwd_root="/workspace",
            ),
        )

    def test_t06_unlisted_executable_and_cwd_escape_fail_closed(self):
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
        )
        assert_code(
            self, "PROCESS_EXECUTABLE_DENIED", plan_process_invocation,
            "/usr/bin/python3", ["-V"], cwd="/workspace",
            env={}, provenance="test", policy=policy,
        )
        assert_code(
            self, "PROCESS_CWD_OUT_OF_BOUNDS", plan_process_invocation,
            "/usr/bin/git", ["status"], cwd="/workspace-escape",
            env={}, provenance="test", policy=policy,
        )

    def test_t06_environment_is_allowlisted_and_values_are_not_retained_in_audit_plan(self):
        secret = "super-secret-sentinel"
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
            allowed_env_keys=("TOKEN",),
        )
        plan = plan_process_invocation(
            "/usr/bin/git", ["status"], cwd="/workspace",
            env={"TOKEN": secret}, provenance="test", policy=policy,
        )
        self.assertNotIn(secret, repr(plan))
        self.assertNotIn(secret, json.dumps(plan.audit_record(), sort_keys=True))
        assert_code(
            self, "PROCESS_ENV_DENIED", plan_process_invocation,
            "/usr/bin/git", ["status"], cwd="/workspace",
            env={"NOT_ALLOWED": "x"}, provenance="test", policy=policy,
        )

    def test_t06_shell_metacharacters_remain_literal_tokens_without_interpolation(self):
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
        )
        hostile = ["status", ";rm -rf /", "$(id)", "`id`", "a && b", "x|y", "$HOME"]
        plan = plan_process_invocation(
            "/usr/bin/git", hostile, cwd="/workspace",
            env={}, provenance="test", policy=policy,
        )
        self.assertEqual(plan.argv, tuple(hostile))
        self.assertFalse(plan.shell)

    def test_t06_nul_and_policy_limits_are_rejected(self):
        policy = ProcessPolicy(
            allowed_executables=("/usr/bin/git",),
            allowed_cwd_root="/workspace",
        )
        assert_code(
            self, "PROCESS_NUL_FORBIDDEN", plan_process_invocation,
            "/usr/bin/git", ["status\x00evil"], cwd="/workspace",
            env={}, provenance="test", policy=policy,
        )
        assert_code(
            self, "PROCESS_POLICY_INVALID", plan_process_invocation,
            "/usr/bin/git", ["status"], cwd="/workspace",
            env={}, provenance="test",
            policy=ProcessPolicy(
                allowed_executables=("/usr/bin/git",),
                allowed_cwd_root="/workspace",
                timeout_seconds=9999,
            ),
        )


if __name__ == "__main__":
    unittest.main()
