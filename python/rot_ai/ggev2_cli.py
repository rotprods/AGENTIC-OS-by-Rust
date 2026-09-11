from __future__ import annotations

import argparse
import json
from pathlib import Path

from rot_ai.ggev2 import compile_realtime_state


def _read(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile /GGEV2 realtime derived state")
    parser.add_argument("--project-state", required=True)
    parser.add_argument("--observations", required=True, help="JSON object with source_revision and observations[]")
    parser.add_argument("--governance", required=True)
    parser.add_argument("--quality-gates", required=True)
    parser.add_argument("--output", default="ggev2/REALTIME_STATE.json")
    parser.add_argument("--projection-revision", type=int, default=1)
    args = parser.parse_args()

    project_state = _read(args.project_state)
    observation_input = _read(args.observations)
    governance = _read(args.governance)
    quality_gates = _read(args.quality_gates)

    source_revision = observation_input.get("source_revision")
    observations = observation_input.get("observations")
    if not isinstance(source_revision, str):
        raise SystemExit("observations.source_revision must be a string")
    if not isinstance(observations, list):
        raise SystemExit("observations.observations must be an array")

    compiled = compile_realtime_state(
        project_state=project_state,
        source_revision=source_revision,
        source_observations=observations,
        governance=governance,
        quality_gates=quality_gates,
        projection_revision=args.projection_revision,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(compiled, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GGEV2 {compiled['freshness']} {compiled['state_hash']} -> {destination}")


if __name__ == "__main__":
    main()
