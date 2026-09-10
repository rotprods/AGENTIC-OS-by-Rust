from __future__ import annotations

from typing import Any, Iterable

from .survival import SurvivalContractError


PASS = "PASS"
NON_PASS = {"FAIL", "SKIPPED", "CANCELLED", "NOT_RUN"}


def assert_promotion_evidence(
    tests: list[dict[str, Any]], *, candidate_source_sha: str,
    required_test_ids: Iterable[str], require_evidence_hash: bool = False,
) -> None:
    """Fail closed unless required evidence proves the exact candidate revision.

    This is a promotion preflight, not a generic checkpoint validator. Historical
    checkpoint evidence may legitimately reference older revisions, but it cannot
    be reused to promote a different candidate.
    """
    if not _is_git_sha(candidate_source_sha):
        raise SurvivalContractError("candidate_source_sha must be lowercase git SHA-1 hex")
    if type(tests) is not list:
        raise SurvivalContractError("promotion tests must be list")

    required = list(required_test_ids)
    if not required or any(not isinstance(test_id, str) or not test_id for test_id in required):
        raise SurvivalContractError("required_test_ids must be non-empty strings")
    if len(set(required)) != len(required):
        raise SurvivalContractError("required_test_ids must be unique")

    by_id: dict[str, list[dict[str, Any]]] = {}
    for item in tests:
        if type(item) is not dict:
            raise SurvivalContractError("promotion evidence item must be object")
        test_id = item.get("test_id")
        if not isinstance(test_id, str) or not test_id:
            raise SurvivalContractError("promotion evidence test_id required")
        by_id.setdefault(test_id, []).append(item)

    for test_id in required:
        matches = by_id.get(test_id, [])
        if len(matches) != 1:
            raise SurvivalContractError(f"promotion evidence must contain exactly one result for {test_id}")
        item = matches[0]
        status = item.get("status")
        if status != PASS:
            if status in NON_PASS:
                raise SurvivalContractError(f"promotion evidence {test_id} is {status}, not PASS")
            raise SurvivalContractError(f"promotion evidence {test_id} has invalid status")
        if item.get("source_sha") != candidate_source_sha:
            raise SurvivalContractError(f"promotion evidence {test_id} is bound to a different source revision")
        run_id = item.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise SurvivalContractError(f"promotion evidence {test_id} missing run_id")
        if require_evidence_hash and not _is_hash(item.get("evidence_hash")):
            raise SurvivalContractError(f"promotion evidence {test_id} missing artifact/evidence hash")


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71 and all(
        char in "0123456789abcdef" for char in value[7:]
    )


def _is_git_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(char in "0123456789abcdef" for char in value)
