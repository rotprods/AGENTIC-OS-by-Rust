from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


class PromotionReadinessError(ValueError):
    pass


def _policy(policy: dict[str, Any]) -> tuple[str, str, set[str], dict[str, bool]]:
    if policy.get("schema_version") != "1":
        raise PromotionReadinessError("unsupported policy schema_version")
    if policy.get("authority") != "POLICY_SPECIFICATION_ONLY" or policy.get("promotion_authority") is not False:
        raise PromotionReadinessError("policy must be non-authoritative")
    if policy.get("evaluation") != "FAIL_CLOSED":
        raise PromotionReadinessError("policy must fail closed")
    repository, branch = policy.get("repository"), policy.get("branch")
    contexts = policy.get("required_check_contexts")
    controls = policy.get("required_controls")
    if not isinstance(repository, str) or "/" not in repository:
        raise PromotionReadinessError("invalid repository")
    if not isinstance(branch, str) or not branch:
        raise PromotionReadinessError("invalid branch")
    if not isinstance(contexts, list) or not contexts or any(not isinstance(x, str) or not x for x in contexts):
        raise PromotionReadinessError("invalid required_check_contexts")
    if len(contexts) != len(set(contexts)):
        raise PromotionReadinessError("required_check_contexts must be unique")
    required = {
        "pull_request",
        "prevent_force_push",
        "prevent_deletion",
        "required_signatures",
        "strict_status_checks",
        "enforce_admins",
    }
    if not isinstance(controls, dict) or set(controls) != required or any(not isinstance(v, bool) for v in controls.values()):
        raise PromotionReadinessError("invalid required_controls")
    return repository, branch, set(contexts), controls


def _successful_checks(snapshot: dict[str, Any]) -> set[str]:
    runs = snapshot.get("check_runs")
    if not isinstance(runs, list):
        return set()
    return {
        item["name"]
        for item in runs
        if isinstance(item, dict)
        and isinstance(item.get("name"), str)
        and item.get("status") == "completed"
        and item.get("conclusion") == "success"
    }


def _classic(policy_checks: set[str], controls: dict[str, bool], snapshot: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    protection = snapshot.get("classic_protection")
    if not isinstance(protection, dict):
        return False, {"available": False}
    required = protection.get("required_status_checks")
    contexts: set[str] = set()
    strict = False
    if isinstance(required, dict):
        strict = required.get("strict") is True
        raw = required.get("contexts")
        if isinstance(raw, list):
            contexts.update(x for x in raw if isinstance(x, str))
        raw = required.get("checks")
        if isinstance(raw, list):
            contexts.update(
                x["context"] for x in raw
                if isinstance(x, dict) and isinstance(x.get("context"), str)
            )
    observed = {
        "available": True,
        "contexts": sorted(contexts),
        "strict_status_checks": strict,
        "pull_request": isinstance(protection.get("required_pull_request_reviews"), dict),
        "prevent_force_push": isinstance(protection.get("allow_force_pushes"), dict)
        and protection["allow_force_pushes"].get("enabled") is False,
        "prevent_deletion": isinstance(protection.get("allow_deletions"), dict)
        and protection["allow_deletions"].get("enabled") is False,
        "required_signatures": snapshot.get("classic_required_signatures") is True,
        "enforce_admins": isinstance(protection.get("enforce_admins"), dict)
        and protection["enforce_admins"].get("enabled") is True,
    }
    ok = policy_checks.issubset(contexts)
    for name, required_control in controls.items():
        if required_control and name != "strict_status_checks":
            ok = ok and observed[name] is True
    if controls["strict_status_checks"]:
        ok = ok and strict
    return ok, observed


def _applies(ruleset: dict[str, Any], branch: str, default_branch: str | None) -> bool:
    if ruleset.get("target") != "branch" or ruleset.get("enforcement") != "active":
        return False
    ref_name = (ruleset.get("conditions") or {}).get("ref_name")
    if not isinstance(ref_name, dict):
        return False
    include, exclude = ref_name.get("include"), ref_name.get("exclude", [])
    if not isinstance(include, list) or not include or not isinstance(exclude, list):
        return False
    ref = f"refs/heads/{branch}"

    def match(value: Any) -> bool:
        return isinstance(value, str) and (
            value in {"~ALL", ref, branch}
            or (value == "~DEFAULT_BRANCH" and default_branch == branch)
        )

    return any(match(x) for x in include) and not any(match(x) for x in exclude)


def _rulesets(policy_checks: set[str], controls: dict[str, bool], snapshot: dict[str, Any], branch: str) -> tuple[bool, dict[str, Any]]:
    all_rulesets = snapshot.get("rulesets")
    default_branch = snapshot.get("default_branch")
    if not isinstance(all_rulesets, list):
        all_rulesets = []
    applicable = [
        x for x in all_rulesets
        if isinstance(x, dict) and _applies(x, branch, default_branch if isinstance(default_branch, str) else None)
    ]
    types: set[str] = set()
    contexts: set[str] = set()
    strict = False
    bypass = False
    for ruleset in applicable:
        bypass = bypass or bool(ruleset.get("bypass_actors"))
        rules = ruleset.get("rules")
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, dict) or not isinstance(rule.get("type"), str):
                continue
            types.add(rule["type"])
            if rule["type"] == "required_status_checks":
                params = rule.get("parameters")
                if isinstance(params, dict):
                    strict = strict or params.get("strict_required_status_checks_policy") is True
                    checks = params.get("required_status_checks")
                    if isinstance(checks, list):
                        contexts.update(
                            x["context"] for x in checks
                            if isinstance(x, dict) and isinstance(x.get("context"), str)
                        )
    observed = {
        "applicable_ids": [x.get("id") for x in applicable],
        "rule_types": sorted(types),
        "contexts": sorted(contexts),
        "strict_status_checks": strict,
        "bypass_actors_present": bypass,
    }
    ok = bool(applicable) and policy_checks.issubset(contexts)
    required_types = {
        "pull_request": "pull_request",
        "prevent_force_push": "non_fast_forward",
        "prevent_deletion": "deletion",
        "required_signatures": "required_signatures",
    }
    for control, rule_type in required_types.items():
        if controls[control]:
            ok = ok and rule_type in types
    if controls["strict_status_checks"]:
        ok = ok and strict
    if controls["enforce_admins"]:
        ok = ok and not bypass
    return ok, observed


def evaluate_promotion_readiness(policy: dict[str, Any], snapshot: dict[str, Any], candidate_sha: str) -> dict[str, Any]:
    repository, branch, required_checks, controls = _policy(policy)
    blockers: list[dict[str, str]] = []

    def block(code: str, detail: str) -> None:
        blockers.append({"code": code, "detail": detail})

    if snapshot.get("repository") != repository:
        block("REPOSITORY_MISMATCH", "repository does not match policy")
    if snapshot.get("branch") != branch:
        block("BRANCH_MISMATCH", "branch does not match policy")
    if snapshot.get("head_sha") != candidate_sha:
        block("HEAD_MISMATCH", "candidate SHA is not the live branch head")
    if policy.get("required_head_signature") is True and snapshot.get("head_verified") is not True:
        block("HEAD_SIGNATURE_UNVERIFIED", "candidate head commit is not cryptographically verified")

    successes = _successful_checks(snapshot)
    missing = sorted(required_checks - successes)
    if missing:
        block("EXACT_HEAD_CHECKS_MISSING", "missing successful exact-head checks: " + ", ".join(missing))

    classic_ok, classic_observed = _classic(required_checks, controls, snapshot)
    ruleset_ok, ruleset_observed = _rulesets(required_checks, controls, snapshot, branch)
    mode = "classic_branch_protection" if classic_ok else "repository_ruleset" if ruleset_ok else None
    if mode is None:
        block("PROMOTION_ENFORCEMENT_MISSING", "required protection/ruleset controls are not enforced")

    ready = not blockers
    return {
        "schema_version": "1",
        "authority": "DERIVED_NON_AUTHORITATIVE",
        "promotion_authority": False,
        "repository": repository,
        "branch": branch,
        "candidate_sha": candidate_sha,
        "ready": ready,
        "status": "READY" if ready else "BLOCKED",
        "enforcement_mode": mode,
        "blockers": blockers,
        "observations": {
            "head_verified": snapshot.get("head_verified") is True,
            "successful_check_contexts": sorted(successes),
            "classic_branch_protection": classic_observed,
            "repository_rulesets": ruleset_observed,
        },
    }


def _get(path: str, token: str | None, allow_404: bool = False) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "rot-promotion-readiness-v1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request("https://api.github.com" + path, headers=headers), timeout=20) as response:
            return json.load(response)
    except HTTPError as exc:
        if allow_404 and exc.code == 404:
            return None
        raise PromotionReadinessError(f"GitHub API HTTP {exc.code}: {path}") from exc


def collect_live_snapshot(policy: dict[str, Any], candidate_sha: str, token: str | None = None) -> dict[str, Any]:
    repository, branch, _, _ = _policy(policy)
    owner, repo = repository.split("/", 1)
    encoded_branch = quote(branch, safe="")
    repository_data = _get(f"/repos/{owner}/{repo}", token)
    branch_data = _get(f"/repos/{owner}/{repo}/branches/{encoded_branch}", token)
    checks = _get(f"/repos/{owner}/{repo}/commits/{quote(candidate_sha, safe='')}/check-runs?per_page=100", token)
    protection = _get(f"/repos/{owner}/{repo}/branches/{encoded_branch}/protection", token, True)
    signatures = _get(
        f"/repos/{owner}/{repo}/branches/{encoded_branch}/protection/required_signatures",
        token,
        True,
    )
    summaries = _get(f"/repos/{owner}/{repo}/rulesets?includes_parents=false&per_page=100", token)
    rulesets: list[dict[str, Any]] = []
    if isinstance(summaries, list):
        for summary in summaries:
            if isinstance(summary, dict) and summary.get("target") == "branch" and isinstance(summary.get("id"), int):
                detail = _get(f"/repos/{owner}/{repo}/rulesets/{summary['id']}", token)
                if isinstance(detail, dict):
                    rulesets.append(detail)

    verification = (((branch_data or {}).get("commit") or {}).get("commit") or {}).get("verification") or {}
    raw_checks = checks.get("check_runs", []) if isinstance(checks, dict) else []
    return {
        "repository": repository,
        "branch": branch,
        "default_branch": repository_data.get("default_branch") if isinstance(repository_data, dict) else None,
        "head_sha": (branch_data.get("commit") or {}).get("sha") if isinstance(branch_data, dict) else None,
        "head_verified": verification.get("verified") is True,
        "classic_protection": protection,
        "classic_required_signatures": isinstance(signatures, dict) and signatures.get("enabled") is True,
        "rulesets": rulesets,
        "check_runs": [
            {"name": x.get("name"), "status": x.get("status"), "conclusion": x.get("conclusion")}
            for x in raw_checks if isinstance(x, dict)
        ],
    }


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise PromotionReadinessError(f"{path} must contain a JSON object")
    return value
