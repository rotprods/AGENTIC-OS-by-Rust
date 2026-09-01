#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rot_contracts.promotion_readiness import (
    PromotionReadinessError,
    collect_live_snapshot,
    evaluate_promotion_readiness,
    load_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed GitHub promotion control-plane readiness verifier.")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--candidate-sha", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--live", action="store_true")
    source.add_argument("--snapshot")
    parser.add_argument("--output")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    try:
        policy = load_json(args.policy)
        snapshot = (
            collect_live_snapshot(policy, args.candidate_sha, os.environ.get("GITHUB_TOKEN"))
            if args.live
            else load_json(args.snapshot)
        )
        report = evaluate_promotion_readiness(policy, snapshot, args.candidate_sha)
    except (PromotionReadinessError, OSError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": "1",
            "authority": "DERIVED_NON_AUTHORITATIVE",
            "promotion_authority": False,
            "ready": False,
            "status": "ERROR",
            "blockers": [{"code": "READINESS_EVALUATION_ERROR", "detail": str(exc)}],
        }

    rendered = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        Path(args.output).write_text(rendered)
    print(rendered, end="")
    if args.report_only:
        return 0
    return 0 if report.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
