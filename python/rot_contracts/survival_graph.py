from __future__ import annotations

from typing import Any

from .canonical_json import hash_canonical
from .survival import SurvivalContractError, reduce_events, verify_checkpoint


def build_survival_projection(state: dict[str, Any], *, checkpoint: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a deterministic, read-only COS-compatible projection from canonical Survival state.

    The returned graph is a cache/query artifact only. It contains its source state hash and
    event horizon and exposes no mutation callback or authority transition primitive.
    """
    canonical = reduce_events(state, [])
    state_hash = hash_canonical(canonical)
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}

    def node(node_id: str, node_type: str, **properties: Any) -> None:
        existing = nodes.get(node_id)
        candidate = {"id": node_id, "type": node_type, "properties": properties}
        if existing is not None and existing != candidate:
            raise SurvivalContractError(f"conflicting projection node {node_id}")
        nodes[node_id] = candidate

    def edge(source: str, relation: str, target: str, *, cos_levels: tuple[str, ...], **properties: Any) -> None:
        if source not in nodes or target not in nodes:
            raise SurvivalContractError("projection edge endpoints must exist")
        key = (source, relation, target)
        candidate = {
            "source": source,
            "relation": relation,
            "target": target,
            "cos_levels": sorted(set(cos_levels)),
            "properties": properties,
        }
        existing = edges.get(key)
        if existing is not None and existing != candidate:
            raise SurvivalContractError(f"conflicting projection edge {source} {relation} {target}")
        edges[key] = candidate

    project_id = canonical["project_id"]
    objective_id = canonical["current_objective_id"]
    node(project_id, "Project", north_star=canonical["north_star"], authority_state=canonical["authority_state"])
    node(objective_id, "Objective")
    edge(project_id, "HAS_CURRENT_OBJECTIVE", objective_id, cos_levels=("L0", "L1", "L2"))

    for workstream_id in canonical["active_workstreams"]:
        node(workstream_id, "Workstream", status="ACTIVE")
        edge(project_id, "HAS_ACTIVE_WORKSTREAM", workstream_id, cos_levels=("L0", "L1", "L13", "L15"))
        edge(workstream_id, "SERVES", objective_id, cos_levels=("L1", "L3"))

    for claim_id in canonical["active_claims"]:
        node(claim_id, "Claim", status="ACTIVE")
        edge(claim_id, "CONSTRAINS", project_id, cos_levels=("L3", "L13", "L15"))

    for blocker_id in canonical["blockers"]:
        node(blocker_id, "Blocker")
        edge(blocker_id, "BLOCKS", objective_id, cos_levels=("L1", "L3", "L15"))

    for capability_id in canonical["verified_capabilities"]:
        node(capability_id, "Capability", authority="VERIFIED")
        edge(project_id, "HAS_CAPABILITY", capability_id, cos_levels=("L0", "L8", "L9"), authority="VERIFIED")

    for capability_id in canonical["unverified_capabilities"]:
        node(capability_id, "Capability", authority="UNVERIFIED")
        edge(project_id, "HAS_CAPABILITY", capability_id, cos_levels=("L0", "L8", "L9"), authority="UNVERIFIED")

    for decision_id in canonical["decisions"]:
        node(decision_id, "Decision", status="ACCEPTED")
        edge(decision_id, "CONSTRAINS", project_id, cos_levels=("L3", "L8", "L9", "L15"))

    previous_action: str | None = None
    for index, text in enumerate(canonical["next_safe_actions"]):
        action_id = f"{project_id}/next-action/{index}"
        node(action_id, "Task", ordinal=index, text=text, authority="ADVISORY")
        edge(objective_id, "HAS_NEXT_ACTION", action_id, cos_levels=("L1", "L15"), ordinal=index)
        if previous_action is not None:
            edge(previous_action, "NEXT_AFTER", action_id, cos_levels=("L1", "L3", "L15"))
        previous_action = action_id

    checkpoint_hash = None
    if checkpoint is not None:
        verify_checkpoint(checkpoint, state=canonical)
        checkpoint_id = checkpoint["checkpoint_id"]
        checkpoint_hash = checkpoint["checkpoint_hash"]
        node(
            checkpoint_id,
            "Checkpoint",
            checkpoint_hash=checkpoint_hash,
            state_hash=checkpoint["state_hash"],
            event_watermark=checkpoint["event_watermark"],
        )
        edge(checkpoint_id, "SNAPSHOTS", project_id, cos_levels=("L6", "L12", "L15"))
        agent_id = checkpoint["agent_id"]
        session_id = checkpoint["session_id"]
        node(agent_id, "Agent")
        node(session_id, "Session")
        edge(agent_id, "HAS_SESSION", session_id, cos_levels=("L13",))
        edge(session_id, "PRODUCED", checkpoint_id, cos_levels=("L6", "L12", "L13"))
        if checkpoint["workstream_id"] in nodes:
            edge(session_id, "EXECUTED", checkpoint["workstream_id"], cos_levels=("L13", "L15"))

    graph = {
        "schema_version": "1",
        "authority": "DERIVED_PROJECTION_ONLY",
        "project_id": project_id,
        "source": {
            "observed_source_sha": canonical["observed_source_sha"],
            "event_watermark": canonical["event_watermark"],
            "state_hash": state_hash,
            "checkpoint_hash": checkpoint_hash,
        },
        "nodes": sorted(nodes.values(), key=lambda item: (item["type"], item["id"])),
        "edges": sorted(edges.values(), key=lambda item: (item["source"], item["relation"], item["target"])),
    }
    graph["projection_hash"] = hash_canonical(graph)
    return graph


def verify_projection(projection: dict[str, Any], state: dict[str, Any], *, checkpoint: dict[str, Any] | None = None) -> None:
    if type(projection) is not dict:
        raise SurvivalContractError("projection must be object")
    expected = build_survival_projection(state, checkpoint=checkpoint)
    if projection != expected:
        raise SurvivalContractError("projection rebuild mismatch")
    if projection.get("authority") != "DERIVED_PROJECTION_ONLY":
        raise SurvivalContractError("projection authority escalation")
