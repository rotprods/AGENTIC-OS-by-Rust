from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from rot_contracts.canonical_json import hash_canonical
from .ggev2_incidents import correlate_signals

SUBJECT_RE = re.compile(
    r"^\[(?P<repo>[^\]]+)\]\s+(?:(?:PR\s+)?Run failed):\s+(?P<workflow>.+?)\s+-\s+.+?\s+\((?P<sha>[0-9a-fA-F]{7,40})\)$"
)


class BackfillError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedFailureSignal:
    signal_id: str
    repo: str
    workflow: str
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
    return ParsedFailureSignal(
        signal_id=signal_id,
        repo=match.group("repo"),
        workflow=match.group("workflow").strip(),
        short_sha=match.group("sha").lower(),
        observed_at=message.get("email_ts") if isinstance(message.get("email_ts"), str) else None,
    )


def resolve_page(
    messages: Iterable[dict[str, Any]],
    *,
    resolve_sha: Callable[[str, str], str | None],
    current_heads: dict[str, str],
    current_ci: dict[tuple[str, str], str] | None = None,
    next_page_token: str | None = None,
) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    parse_failures: list[dict[str, str]] = []
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
        signals.append(
            {
                "signal_id": parsed.signal_id,
                "source": "gmail:github-notification",
                "repo": parsed.repo,
                "workflow": parsed.workflow,
                "sha": full_sha,
                "failure_family": "WORKFLOW_FAILURE",
                "observed_at": parsed.observed_at,
                "short_sha": parsed.short_sha,
            }
        )

    correlation = correlate_signals(signals, current_heads=current_heads, current_ci=current_ci)
    output = {
        "schema_version": "1",
        "authority_class": "DERIVED_SIGNAL_ONLY",
        "page_size": len(signals) + len(parse_failures),
        "resolved_signals": len(signals) - sum(1 for signal in signals if signal["sha"] is None),
        "unresolved_signals": sum(1 for signal in signals if signal["sha"] is None),
        "parse_failures": parse_failures,
        "next_page_token": next_page_token,
        "correlation": correlation,
    }
    output["checkpoint_hash"] = hash_canonical(output)
    return output
