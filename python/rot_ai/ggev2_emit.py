from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .ggev2_swarm import TelemetryEvent


def main() -> int:
    p = argparse.ArgumentParser(description="Emit one validated GGEV2 observation record. Observation only; grants no authority.")
    p.add_argument("event_type", choices=["BOOT", "CLAIM", "HEARTBEAT", "EVIDENCE", "PREFLIGHT", "HANDOFF"])
    p.add_argument("--agent-id", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--project-id", required=True)
    p.add_argument("--objective-id", required=True)
    p.add_argument("--workstream-id")
    p.add_argument("--repo", default="rotprods/AGENTIC-OS-by-Rust")
    p.add_argument("--branch", required=True)
    p.add_argument("--head-sha", required=True)
    p.add_argument("--watermark", type=int)
    p.add_argument("--claim-id")
    p.add_argument("--fencing-generation", type=int)
    p.add_argument("--state-hash")
    p.add_argument("--next-action")
    p.add_argument("--freshness", default="UNKNOWN", choices=["FRESH", "STALE", "UNKNOWN", "BLOCKED"])
    p.add_argument("--resource-scope", action="append", default=[])
    p.add_argument("--semantic-scope", action="append", default=[])
    p.add_argument("--evidence-id", action="append", default=[])
    args = p.parse_args()

    event = TelemetryEvent(
        event_type=args.event_type,
        agent_id=args.agent_id,
        session_id=args.session_id,
        project_id=args.project_id,
        objective_id=args.objective_id,
        workstream_id=args.workstream_id,
        repo=args.repo,
        branch=args.branch,
        head_sha=args.head_sha,
        observed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        claim_id=args.claim_id,
        fencing_generation=args.fencing_generation,
        event_watermark=args.watermark,
        state_hash=args.state_hash,
        semantic_scopes=tuple(args.semantic_scope),
        resource_scopes=tuple(args.resource_scope),
        evidence_ids=tuple(args.evidence_id),
        next_action=args.next_action,
        freshness=args.freshness,
    )
    print(json.dumps(event.as_record(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
