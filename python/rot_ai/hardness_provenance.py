from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping

from .hardness import EvidenceRecord, HardnessError, WorkContext

TRUSTED_PROVIDERS = {"github-actions", "hardness-local-verifier"}
_QUALIFIED_EVIDENCE_SEAL = object()


@dataclass(frozen=True)
class ProviderObservation:
    provider: str
    gate: str
    repo: str
    ref: str
    sha: str
    conclusion: str
    provider_run_id: str
    artifact_hash: str | None = None


@dataclass(frozen=True, init=False)
class QualifiedEvidence:
    record: EvidenceRecord
    provider: str
    provider_run_id: str
    observation_hash: str
    provenance_verified: bool

    def __init__(
        self,
        record: EvidenceRecord,
        provider: str,
        provider_run_id: str,
        observation_hash: str,
        *,
        _seal: object | None = None,
    ) -> None:
        if _seal is not _QUALIFIED_EVIDENCE_SEAL:
            raise HardnessError(
                "QUALIFIED_EVIDENCE_CONSTRUCTION_FORBIDDEN",
                "QualifiedEvidence must be minted by a trusted verifier",
            )
        object.__setattr__(self, "record", record)
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "provider_run_id", provider_run_id)
        object.__setattr__(self, "observation_hash", observation_hash)
        object.__setattr__(self, "provenance_verified", True)


def qualify_provider_observation(*, context: WorkContext, observation: ProviderObservation) -> QualifiedEvidence:
    if observation.provider not in TRUSTED_PROVIDERS:
        raise HardnessError("UNTRUSTED_EVIDENCE_PROVIDER", observation.provider)
    if observation.repo != context.repo or observation.ref != context.ref or observation.sha != context.candidate_sha:
        raise HardnessError("EVIDENCE_IDENTITY_MISMATCH", "provider observation is not bound to candidate repo+ref+sha")
    if not observation.provider_run_id.strip():
        raise HardnessError("MISSING_PROVIDER_RUN_ID", "provider run identity is required")
    if observation.conclusion != "success":
        raise HardnessError("PROVIDER_GATE_NOT_SUCCESS", observation.conclusion)
    payload = {
        "provider": observation.provider,
        "gate": observation.gate,
        "repo": observation.repo,
        "ref": observation.ref,
        "sha": observation.sha,
        "conclusion": observation.conclusion,
        "provider_run_id": observation.provider_run_id,
        "artifact_hash": observation.artifact_hash,
    }
    observation_hash = _hash(payload)
    record = EvidenceRecord(
        gate=observation.gate,
        repo=observation.repo,
        ref=observation.ref,
        sha=observation.sha,
        status="PASS",
        evidence_id=f"qualified:{observation.provider}:{observation.provider_run_id}:{observation.gate}",
        artifact_hash=observation.artifact_hash,
    )
    return QualifiedEvidence(
        record,
        observation.provider,
        observation.provider_run_id,
        observation_hash,
        _seal=_QUALIFIED_EVIDENCE_SEAL,
    )


def qualify_github_run_payload(*, context: WorkContext, gate: str, payload: Mapping[str, object]) -> QualifiedEvidence:
    head_sha = str(payload.get("head_sha", ""))
    conclusion = str(payload.get("conclusion", ""))
    run_id = str(payload.get("id", ""))
    head_branch = str(payload.get("head_branch", ""))
    repository = payload.get("repository")
    full_name = repository.get("full_name") if isinstance(repository, Mapping) else None
    observation = ProviderObservation(
        provider="github-actions",
        gate=gate,
        repo=str(full_name or ""),
        ref=head_branch,
        sha=head_sha,
        conclusion=conclusion,
        provider_run_id=run_id,
    )
    return qualify_provider_observation(context=context, observation=observation)


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()
