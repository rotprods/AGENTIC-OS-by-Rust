from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from .survival import SurvivalContractError, verify_checkpoint


_CHECKPOINT_PREFIX = "rot://checkpoint/agentic-os/"
_CHECKPOINT_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,159}$")


def resolve_latest_checkpoint_path(root: Path, state: dict[str, Any]) -> Path:
    """Resolve the canonical checkpoint path without allowing path escape or guessing."""
    checkpoint_id = state.get("latest_checkpoint_id")
    if not isinstance(checkpoint_id, str) or not checkpoint_id.startswith(_CHECKPOINT_PREFIX):
        raise SurvivalContractError(
            "latest_checkpoint_id must use canonical agentic-os checkpoint URI",
            code="INVALID_CHECKPOINT_ID",
        )
    slug = checkpoint_id[len(_CHECKPOINT_PREFIX):]
    if not _CHECKPOINT_SLUG.fullmatch(slug):
        raise SurvivalContractError(
            "latest_checkpoint_id contains invalid checkpoint slug",
            code="INVALID_CHECKPOINT_ID",
        )

    checkpoint_dir = (root / "state" / "checkpoints").resolve()
    candidate = (checkpoint_dir / f"{slug}.json").resolve()
    if candidate.parent != checkpoint_dir:
        raise SurvivalContractError("checkpoint path escaped canonical directory", code="CHECKPOINT_PATH_ESCAPE")
    if not candidate.is_file():
        raise SurvivalContractError("latest checkpoint file does not exist", code="CHECKPOINT_NOT_FOUND")
    return candidate


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
    if parent is not None and not isinstance(parent, str):
        raise SurvivalContractError("parent_checkpoint_id must be string or null", code="INVALID_CHECKPOINT_ID")

    sealed_state = deepcopy(state)
    sealed_state["latest_checkpoint_id"] = parent
    verify_checkpoint(checkpoint, state=sealed_state)
