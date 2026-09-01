from __future__ import annotations

from typing import Any

from .survival import SurvivalContractError


LEGACY_RESOLUTION_STATES = {"PINNED", "UNRESOLVED"}
RESOLUTION_STATES = {"PINNED", "CANDIDATE_PINNED", "UNRESOLVED"}
LOCATOR_STATES = {"PINNED", "CANDIDATE_PINNED"}


def validate_external_authority_manifest(manifest: dict[str, Any]) -> None:
    if type(manifest) is not dict:
        raise SurvivalContractError("external authority manifest must be object")
    schema_version = manifest.get("schema_version")
    if schema_version not in {"1", "2"}:
        raise SurvivalContractError("unsupported external authority manifest schema")
    if manifest.get("authority") != "REFERENCE_MANIFEST_ONLY":
        raise SurvivalContractError("external authority manifest cannot claim runtime authority")
    if manifest.get("promotion_policy") != "FAIL_CLOSED_ON_REQUIRED_UNRESOLVED_OR_DRIFT":
        raise SurvivalContractError("external authority manifest promotion policy must fail closed")
    authorities = manifest.get("authorities")
    if type(authorities) is not list or not authorities:
        raise SurvivalContractError("external authority manifest requires authorities")

    allowed_states = LEGACY_RESOLUTION_STATES if schema_version == "1" else RESOLUTION_STATES
    seen: set[str] = set()
    for item in authorities:
        if type(item) is not dict:
            raise SurvivalContractError("external authority entry must be object")
        authority_id = item.get("authority_id")
        if not isinstance(authority_id, str) or not authority_id:
            raise SurvivalContractError("external authority_id required")
        if authority_id in seen:
            raise SurvivalContractError(f"duplicate external authority {authority_id}")
        seen.add(authority_id)

        role = item.get("role")
        if not isinstance(role, str) or not role:
            raise SurvivalContractError(f"external authority {authority_id} role required")
        status = item.get("resolution_status")
        if status not in allowed_states:
            raise SurvivalContractError(f"external authority {authority_id} resolution status invalid")
        if type(item.get("required_for_promotion")) is not bool:
            raise SurvivalContractError(f"external authority {authority_id} promotion requirement must be boolean")

        blockers = item.get("promotion_blockers")
        if status in LOCATOR_STATES:
            if item.get("source_type") != "github_repository":
                raise SurvivalContractError(f"located authority {authority_id} source_type invalid")
            repo = item.get("repository_full_name")
            ref = item.get("ref")
            sha = item.get("pinned_sha")
            content_path = item.get("content_path")
            if not isinstance(repo, str) or "/" not in repo:
                raise SurvivalContractError(f"located authority {authority_id} repository required")
            if not isinstance(ref, str) or not ref:
                raise SurvivalContractError(f"located authority {authority_id} ref required")
            if not _is_git_sha(sha):
                raise SurvivalContractError(f"located authority {authority_id} SHA invalid")
            if content_path is not None and not _is_repo_relative_path(content_path):
                raise SurvivalContractError(f"located authority {authority_id} content_path invalid")

            if status == "CANDIDATE_PINNED":
                if schema_version != "2":
                    raise SurvivalContractError("candidate-pinned authorities require manifest schema v2")
                if not _nonempty_string_list(blockers):
                    raise SurvivalContractError(
                        f"candidate-pinned authority {authority_id} requires promotion_blockers"
                    )
            elif blockers not in (None, []):
                raise SurvivalContractError(
                    f"promotion-qualified pinned authority {authority_id} must not carry promotion_blockers"
                )
        else:
            for field in ("repository_full_name", "ref", "pinned_sha", "content_path"):
                if item.get(field) is not None:
                    raise SurvivalContractError(
                        f"unresolved authority {authority_id} must not carry guessed {field}"
                    )
            if blockers not in (None, []):
                raise SurvivalContractError(
                    f"unresolved authority {authority_id} must not carry promotion_blockers"
                )


def assert_external_governance_locators_fresh(
    manifest: dict[str, Any], *, observed_heads: dict[str, str]
) -> None:
    """Verify every exact locator without treating candidate pins as promotion authority."""
    validate_external_authority_manifest(manifest)
    for item in manifest["authorities"]:
        if item["resolution_status"] not in LOCATOR_STATES:
            continue
        _assert_observed_head(item, observed_heads)


def assert_external_governance_ready(
    manifest: dict[str, Any], *, observed_heads: dict[str, str]
) -> None:
    """Fail closed unless every required authority is final-pinned and not drifted.

    `CANDIDATE_PINNED` deliberately separates "we know exactly where the candidate
    lives" from "that candidate is authorized for promotion". `observed_heads` is
    supplied by an operator/tool preflight; this deterministic contract performs no
    network access itself.
    """
    validate_external_authority_manifest(manifest)
    for item in manifest["authorities"]:
        if not item["required_for_promotion"]:
            continue
        authority_id = item["authority_id"]
        status = item["resolution_status"]
        if status == "UNRESOLVED":
            raise SurvivalContractError(
                f"required external authority {authority_id} is unresolved",
                code="GOVERNANCE_AUTHORITY_UNRESOLVED",
            )
        if status == "CANDIDATE_PINNED":
            raise SurvivalContractError(
                f"required external authority {authority_id} is candidate-pinned but not promotion-qualified",
                code="GOVERNANCE_AUTHORITY_NOT_PROMOTION_QUALIFIED",
            )
        _assert_observed_head(item, observed_heads)


def _assert_observed_head(item: dict[str, Any], observed_heads: dict[str, str]) -> None:
    authority_id = item["authority_id"]
    observed = observed_heads.get(authority_id)
    if observed is None:
        raise SurvivalContractError(
            f"required external authority {authority_id} was not observed",
            code="GOVERNANCE_AUTHORITY_UNOBSERVED",
        )
    if not _is_git_sha(observed):
        raise SurvivalContractError(
            f"observed external authority {authority_id} SHA invalid",
            code="GOVERNANCE_AUTHORITY_OBSERVATION_INVALID",
        )
    if observed != item["pinned_sha"]:
        raise SurvivalContractError(
            f"external authority {authority_id} drift detected",
            code="GOVERNANCE_AUTHORITY_DRIFT",
        )


def _nonempty_string_list(value: Any) -> bool:
    return (
        type(value) is list
        and bool(value)
        and all(isinstance(item, str) and bool(item) and len(item) <= 1024 for item in value)
    )


def _is_repo_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 1024:
        return False
    if value.startswith("/") or "\\" in value:
        return False
    parts = value.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _is_git_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )
