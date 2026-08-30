from __future__ import annotations

from typing import Any

from .survival import SurvivalContractError


RESOLUTION_STATES = {"PINNED", "UNRESOLVED"}


def validate_external_authority_manifest(manifest: dict[str, Any]) -> None:
    if type(manifest) is not dict:
        raise SurvivalContractError("external authority manifest must be object")
    if manifest.get("schema_version") != "1":
        raise SurvivalContractError("unsupported external authority manifest schema")
    if manifest.get("authority") != "REFERENCE_MANIFEST_ONLY":
        raise SurvivalContractError("external authority manifest cannot claim runtime authority")
    if manifest.get("promotion_policy") != "FAIL_CLOSED_ON_REQUIRED_UNRESOLVED_OR_DRIFT":
        raise SurvivalContractError("external authority manifest promotion policy must fail closed")
    authorities = manifest.get("authorities")
    if type(authorities) is not list or not authorities:
        raise SurvivalContractError("external authority manifest requires authorities")

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
        if status not in RESOLUTION_STATES:
            raise SurvivalContractError(f"external authority {authority_id} resolution status invalid")
        if type(item.get("required_for_promotion")) is not bool:
            raise SurvivalContractError(f"external authority {authority_id} promotion requirement must be boolean")

        if status == "PINNED":
            if item.get("source_type") != "github_repository":
                raise SurvivalContractError(f"pinned authority {authority_id} source_type invalid")
            repo = item.get("repository_full_name")
            ref = item.get("ref")
            sha = item.get("pinned_sha")
            if not isinstance(repo, str) or "/" not in repo:
                raise SurvivalContractError(f"pinned authority {authority_id} repository required")
            if not isinstance(ref, str) or not ref:
                raise SurvivalContractError(f"pinned authority {authority_id} ref required")
            if not _is_git_sha(sha):
                raise SurvivalContractError(f"pinned authority {authority_id} SHA invalid")
        else:
            for field in ("repository_full_name", "ref", "pinned_sha", "content_path"):
                if item.get(field) is not None:
                    raise SurvivalContractError(
                        f"unresolved authority {authority_id} must not carry guessed {field}"
                    )


def assert_external_governance_ready(
    manifest: dict[str, Any], *, observed_heads: dict[str, str]
) -> None:
    """Fail closed unless every required authority is resolved and not drifted.

    `observed_heads` is supplied by the operator/tool preflight. The deterministic
    contract intentionally performs no network access itself.
    """
    validate_external_authority_manifest(manifest)
    authorities = manifest["authorities"]
    for item in authorities:
        if not item["required_for_promotion"]:
            continue
        authority_id = item["authority_id"]
        if item["resolution_status"] != "PINNED":
            raise SurvivalContractError(f"required external authority {authority_id} is unresolved")
        observed = observed_heads.get(authority_id)
        if observed is None:
            raise SurvivalContractError(f"required external authority {authority_id} was not observed")
        if not _is_git_sha(observed):
            raise SurvivalContractError(f"observed external authority {authority_id} SHA invalid")
        if observed != item["pinned_sha"]:
            raise SurvivalContractError(f"external authority {authority_id} drift detected")


def _is_git_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )
