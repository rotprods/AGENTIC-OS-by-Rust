from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from rot_contracts.canonical_json import hash_canonical
from .ggev2_incidents import correlate_signals

SUBJECT_RE = re.compile(
    r"^\[(?P<repo>[^\]]+)\]\s+(?P<kind>PR run failed|Run failed):\s+"
    r"(?P<workflow>.+?)\s+-\s+(?P<middle>.+?)\s+\((?P<sha>[0-9a-fA-F]{7,40})\)$"
)


class BackfillError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedFailureSignal:
    signal_id: str
    repo: str
    workflow: str
    source_kind: str
    ref_hint: str | None
    pr_title: str | None
    short_sha: str
    observed_at: str | None


def parse_github_failure_email(message: dict[str, Any]) -> ParsedFailureSignal:
    if not isinstance(message, dict):
        raise BackfillError("message must be object")
    signal_id = message.get("id")
    subject = message.get("subject")
    if not isinstance(signal_id, str) or not signal_id or not isinstance(subject, str):
        raise BackfillError("id and subject required")
    match = SUBJECT_RE.match(subject.strip())
    if match is None:
        raise BackfillError("unsupported GitHub failure subject")
    source_kind = "PR_RUN" if match.group("kind") == "PR run failed" else "RUN"
    middle = match.group("middle").strip()
    return ParsedFailureSignal(
        signal_id=signal_id,
        repo=match.group("repo"),
        workflow=match.group("workflow").strip(),
        source_kind=source_kind,
        ref_hint=middle if source_kind == "RUN" else None,
        pr_title=middle if source_kind == "PR_RUN" else None,
        short_sha=match.group("sha").lower(),
        observed_at=message.get("email_ts") if isinstance(message.get("email_ts"), str) else None,
    )


def resolve_page(
    messages: Iterable[dict[str, Any]],
    *,
    resolve_sha: Callable[[str, str], str | None],
    resolve_ref: Callable[[str, str, str, str | None, str | None], str | None] | None = None,
    current_heads: dict[str, str] | None = None,
    current_refs: dict[tuple[str, str], str] | None = None,
    current_ci: dict[tuple[str, ...], str] | None = None,
    next_page_token: str | None = None,
) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    parse_failures: list[dict[str, str]] = []
    ref_resolution_failures: list[dict[str, str]] = []

    for message in messages:
        try:
            parsed = parse_github_failure_email(message)
        except BackfillError as exc:
            parse_failures.append({"signal_id": str(message.get("id") or ""), "reason": str(exc)})
            continue

        full_sha = resolve_sha(parsed.repo, parsed.short_sha)
        if full_sha is not None:
            if len(full_sha) != 40 or any(ch not in "0123456789abcdef" for ch in full_sha):
                raise BackfillError("resolver returned invalid full SHA")

        resolved_ref: str | None = None
        if full_sha is not None:
            if parsed.source_kind == "RUN":
                resolved_ref = parsed.ref_hint
            elif resolve_ref is not None:
                resolved_ref = resolve_ref(
                    parsed.repo,
                    full_sha,
                    parsed.source_kind,
                    parsed.ref_hint,
                    parsed.pr_title,
                )
            if resolved_ref is None:
                ref_resolution_failures.append(
                    {
                        "signal_id": parsed.signal_id,
                        "reason": "REF_UNRESOLVED",
                        "source_kind": parsed.source_kind,
                    }
                )

        signals.append(
            {
                "signal_id": parsed.signal_id,
                "source": "gmail:github-notification",
                "repo": parsed.repo,
                "ref": resolved_ref,
                "workflow": parsed.workflow,
                "sha": full_sha,
                "failure_family": "WORKFLOW_FAILURE",
                "observed_at": parsed.observed_at,
                "short_sha": parsed.short_sha,
                "source_kind": parsed.source_kind,
                "pr_title": parsed.pr_title,
            }
        )

    correlation = correlate_signals(
        signals,
        current_heads=current_heads,
        current_refs=current_refs,
        current_ci=current_ci,
    )
    output = {
        "schema_version": "2",
        "authority_class": "DERIVED_SIGNAL_ONLY",
        "page_size": len(signals) + len(parse_failures),
        "resolved_signals": len(signals) - sum(1 for signal in signals if signal["sha"] is None),
        "unresolved_signals": sum(1 for signal in signals if signal["sha"] is None),
        "resolved_refs": sum(1 for signal in signals if signal["ref"] is not None),
        "unresolved_refs": sum(1 for signal in signals if signal["sha"] is not None and signal["ref"] is None),
        "parse_failures": parse_failures,
        "ref_resolution_failures": ref_resolution_failures,
        "next_page_token": next_page_token,
        "correlation": correlation,
    }
    output["checkpoint_hash"] = hash_canonical(output)
    return output
