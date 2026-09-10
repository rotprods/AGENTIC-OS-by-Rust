from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from .survival import SurvivalContractError, verify_checkpoint


_CHECKPOINT_PREFIX = "rot://checkpoint/agentic-os/"
_CHECKPOINT_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")
_MAX_CHECKPOINT_CHAIN = 1024


def _checkpoint_slug(checkpoint_id: Any) -> str:
    if not isinstance(checkpoint_id, str) or not checkpoint_id.startswith(_CHECKPOINT_PREFIX):
        raise SurvivalContractError(
            "checkpoint id must use canonical agentic-os checkpoint URI",
            code="INVALID_CHECKPOINT_ID",
        )
    slug = checkpoint_id[len(_CHECKPOINT_PREFIX):]
    if not _CHECKPOINT_SLUG.fullmatch(slug):
        raise SurvivalContractError(
            "checkpoint id contains invalid checkpoint slug",
            code="INVALID_CHECKPOINT_ID",
        )
    return slug


def resolve_checkpoint_id_path(root: Path, checkpoint_id: Any, *, require_exists: bool = True) -> Path:
    """Resolve one canonical checkpoint URI to its only allowed repository path."""
    slug = _checkpoint_slug(checkpoint_id)
    checkpoint_dir = (root / "state" / "checkpoints").resolve()
    candidate = (checkpoint_dir / f"{slug}.json").resolve()
    if candidate.parent != checkpoint_dir:
        raise SurvivalContractError("checkpoint path escaped canonical directory", code="CHECKPOINT_PATH_ESCAPE")
    if require_exists and not candidate.is_file():
        raise SurvivalContractError("checkpoint file does not exist", code="CHECKPOINT_NOT_FOUND")
    return candidate


def resolve_latest_checkpoint_path(root: Path, state: dict[str, Any]) -> Path:
    """Resolve the canonical latest checkpoint path without allowing path escape or guessing."""
    try:
        checkpoint_id = state.get("latest_checkpoint_id")
    except AttributeError as exc:
        raise SurvivalContractError("state must be object", code="INVALID_STATE") from exc
    return resolve_checkpoint_id_path(root, checkpoint_id)


def verify_latest_checkpoint_binding(state: dict[str, Any], checkpoint: dict[str, Any]) -> None:
    """Verify the latest checkpoint against the state it sealed before pointer advancement.

    Creating checkpoint C necessarily advances canonical state's `latest_checkpoint_id` from
    C.parent_checkpoint_id to C.checkpoint_id. Hashing the post-advance state into C would be
    self-referential. Therefore C binds the immediately pre-advance state; the live state is
    reconstructed for verification by rewinding only that pointer. Any other state drift still
    fails through `verify_checkpoint`.
    """
    if checkpoint.get("checkpoint_id") != state.get("latest_checkpoint_id"):
        raise SurvivalContractError("latest checkpoint identity mismatch", code="CHECKPOINT_ID_MISMATCH")

    parent = checkpoint.get("parent_checkpoint_id")
    if parent is not None:
        _checkpoint_slug(parent)

    sealed_state = deepcopy(state)
    sealed_state["latest_checkpoint_id"] = parent
    verify_checkpoint(checkpoint, state=sealed_state)


def verify_checkpoint_lineage_topology(root: Path, state: dict[str, Any]) -> list[str]:
    """Verify checkpoint identity/topology without promoting historical payloads to authority.

    Historical checkpoints may deliberately preserve failed construction evidence. Therefore this
    function does not re-certify every historical state/checkpoint hash. It verifies only the
    structural facts required for unambiguous continuity: canonical URI<->filename identity,
    unique IDs, existing parents, one linear ancestry for the selected latest checkpoint, no
    cycles/forks, and no unconsumed child beyond the state pointer.
    """
    checkpoint_dir = (root / "state" / "checkpoints").resolve()
    if not checkpoint_dir.is_dir():
        raise SurvivalContractError("checkpoint directory does not exist", code="CHECKPOINT_DIRECTORY_NOT_FOUND")

    documents: dict[str, dict[str, Any]] = {}
    children: dict[str, list[str]] = {}

    for path in sorted(checkpoint_dir.glob("*.json")):
        try:
            document = json.loads(path.read_text())
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SurvivalContractError(
                f"malformed checkpoint document: {path.name}",
                code="MALFORMED_CHECKPOINT_DOCUMENT",
            ) from exc
        if type(document) is not dict:
            raise SurvivalContractError(
                f"checkpoint document must be object: {path.name}",
                code="MALFORMED_CHECKPOINT_DOCUMENT",
            )

        checkpoint_id = document.get("checkpoint_id")
        canonical_path = resolve_checkpoint_id_path(root, checkpoint_id, require_exists=False)
        if canonical_path != path.resolve():
            raise SurvivalContractError(
                f"checkpoint filename does not match checkpoint_id: {path.name}",
                code="CHECKPOINT_FILENAME_MISMATCH",
            )
        if checkpoint_id in documents:
            raise SurvivalContractError("duplicate checkpoint identity", code="DUPLICATE_CHECKPOINT_ID")

        parent = document.get("parent_checkpoint_id")
        if parent is not None:
            _checkpoint_slug(parent)
            children.setdefault(parent, []).append(checkpoint_id)
        documents[checkpoint_id] = document

    latest = state.get("latest_checkpoint_id") if isinstance(state, dict) else None
    _checkpoint_slug(latest)
    if latest not in documents:
        raise SurvivalContractError("latest checkpoint file does not exist", code="CHECKPOINT_NOT_FOUND")

    lineage: list[str] = []
    seen: set[str] = set()
    current: str | None = latest
    while current is not None:
        if current in seen:
            raise SurvivalContractError("checkpoint parent cycle detected", code="CHECKPOINT_PARENT_CYCLE")
        if len(lineage) >= _MAX_CHECKPOINT_CHAIN:
            raise SurvivalContractError("checkpoint lineage exceeds bounded depth", code="CHECKPOINT_CHAIN_TOO_DEEP")
        document = documents.get(current)
        if document is None:
            raise SurvivalContractError("checkpoint parent is orphaned", code="CHECKPOINT_ORPHAN_PARENT")
        seen.add(current)
        lineage.append(current)
        parent = document.get("parent_checkpoint_id")
        if parent is not None:
            _checkpoint_slug(parent)
            siblings = children.get(parent, [])
            if len(siblings) > 1:
                raise SurvivalContractError("checkpoint lineage fork detected", code="CHECKPOINT_LINEAGE_FORK")
        current = parent

    unconsumed_children = children.get(latest, [])
    if unconsumed_children:
        raise SurvivalContractError(
            "state latest checkpoint pointer is behind an existing child checkpoint",
            code="CHECKPOINT_POINTER_BEHIND",
        )

    return lineage
