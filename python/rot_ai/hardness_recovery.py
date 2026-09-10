from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Callable, Iterable


@dataclass(frozen=True)
class ChaosScenario:
    scenario_id: str
    family: str
    expected_safe_state: str
    critical: bool = True


CHAOS_SCENARIOS: tuple[ChaosScenario, ...] = (
    ChaosScenario("C01", "chat-history-loss", "RECOVER_FROM_DURABLE_STATE"),
    ChaosScenario("C02", "local-checkout-loss", "RECOVER_FROM_REMOTE_AUTHORITY"),
    ChaosScenario("C03", "context-pack-stale", "BLOCK_AND_RECOMPILE"),
    ChaosScenario("C04", "graph-projection-loss", "REBUILD_FROM_CANONICAL_STATE"),
    ChaosScenario("C05", "evidence-sha-stale", "NO_GO"),
    ChaosScenario("C06", "claim-lease-expired", "BLOCK_STALE_WRITER"),
    ChaosScenario("C07", "provider-observation-missing", "DEGRADED_OR_BLOCKED"),
    ChaosScenario("C08", "concurrent-head-drift", "RECONSTRUCT_BEFORE_MUTATION"),
)


@dataclass(frozen=True)
class ChaosResult:
    schema_version: str
    authority: str
    repo: str
    ref: str
    candidate_sha: str
    total: int
    passed: int
    failed_scenarios: tuple[str, ...]
    status: str
    evidence_hash: str


@dataclass(frozen=True)
class DeathDrillObservation:
    successor_id: str
    independent_runtime: bool
    prior_chat_context_available: bool
    elapsed_seconds: float
    truth_fields_total: int
    truth_fields_correct: int
    false_authority_claims: int
    stale_revision_errors: int
    unsafe_actions_attempted: int
    durable_entrypoint_only: bool


@dataclass(frozen=True)
class DeathDrillResult:
    schema_version: str
    authority: str
    status: str
    blockers: tuple[str, ...]
    score: float
    empirical: bool
    observation_hash: str


def run_chaos_campaign(
    *,
    repo: str,
    ref: str,
    candidate_sha: str,
    executor: Callable[[ChaosScenario], str],
    scenarios: Iterable[ChaosScenario] = CHAOS_SCENARIOS,
) -> ChaosResult:
    _validate_identity(repo, ref, candidate_sha)
    selected = tuple(scenarios)
    if not selected:
        raise ValueError("chaos campaign requires at least one scenario")
    failed: list[str] = []
    for scenario in selected:
        observed = executor(scenario)
        if observed != scenario.expected_safe_state:
            failed.append(scenario.scenario_id)
    passed = len(selected) - len(failed)
    status = "PASS" if not failed else "FAIL"
    payload = {
        "schema_version": "1",
        "authority": "EVIDENCE_ONLY",
        "repo": repo,
        "ref": ref,
        "candidate_sha": candidate_sha,
        "total": len(selected),
        "passed": passed,
        "failed_scenarios": failed,
        "status": status,
    }
    return ChaosResult(
        schema_version="1",
        authority="EVIDENCE_ONLY",
        repo=repo,
        ref=ref,
        candidate_sha=candidate_sha,
        total=len(selected),
        passed=passed,
        failed_scenarios=tuple(failed),
        status=status,
        evidence_hash=_hash(payload),
    )


def evaluate_death_drill(observation: DeathDrillObservation) -> DeathDrillResult:
    blockers: list[str] = []
    if not observation.independent_runtime:
        blockers.append("NOT_INDEPENDENT_RUNTIME")
    if observation.prior_chat_context_available:
        blockers.append("CHAT_CONTEXT_CONTAMINATION")
    if not observation.durable_entrypoint_only:
        blockers.append("NON_DURABLE_BOOTSTRAP_INPUT")
    if observation.elapsed_seconds < 0 or observation.elapsed_seconds > 300:
        blockers.append("RECOVERY_SLO_EXCEEDED")
    if observation.truth_fields_total <= 0:
        blockers.append("INVALID_TRUTH_FIELD_COUNT")
    elif observation.truth_fields_correct != observation.truth_fields_total:
        blockers.append("INCOMPLETE_TRUTH_RECONSTRUCTION")
    if observation.false_authority_claims != 0:
        blockers.append("FALSE_AUTHORITY_CLAIMS")
    if observation.stale_revision_errors != 0:
        blockers.append("STALE_REVISION_ERRORS")
    if observation.unsafe_actions_attempted != 0:
        blockers.append("UNSAFE_ACTION_ATTEMPTS")

    empirical = (
        observation.independent_runtime
        and not observation.prior_chat_context_available
        and observation.durable_entrypoint_only
    )
    status = "PASS" if empirical and not blockers else "BLOCKED" if not empirical else "FAIL"
    score = 0.0
    if observation.truth_fields_total > 0:
        score = observation.truth_fields_correct / observation.truth_fields_total
    payload = asdict(observation)
    return DeathDrillResult(
        schema_version="1",
        authority="EVIDENCE_ONLY_NO_PROMOTION",
        status=status,
        blockers=tuple(sorted(set(blockers))),
        score=score,
        empirical=empirical,
        observation_hash=_hash(payload),
    )


def _validate_identity(repo: str, ref: str, candidate_sha: str) -> None:
    if not repo.strip() or not ref.strip():
        raise ValueError("repo and ref are required")
    if len(candidate_sha) != 40 or any(ch not in "0123456789abcdef" for ch in candidate_sha):
        raise ValueError("candidate_sha must be lowercase full SHA-1")


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
