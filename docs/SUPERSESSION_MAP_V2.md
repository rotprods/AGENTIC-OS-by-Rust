# Survival V1 → V2 Supersession Map

Authority: migration/historical map. V1 history remains in PR #2; V2 does not copy obsolete contracts merely to preserve filenames.

| Survival V1 surface (PR #2) | V2 replacement in PR #3 | Rule |
|---|---|---|
| `AGENTS.md` | hardened `AGENTS.md` | V2 extends F1 laws + continuity lifecycle |
| `docs/AGENT_SURVIVAL_PROTOCOL.md` | `docs/AGENT_SURVIVAL_PROTOCOL_V2.md` + `docs/ARCHITECTURE_V2.md` | V1 prose SUPERSEDED |
| `graph/ONTOLOGY.md` | `graph/ONTOLOGY_V2.md` + `graph/projection_manifest.json` | V1 ontology SUPERSEDED |
| `prompts/AGENT_SURVIVAL_METAPROMPT.md` | `prompts/GRAPH_REFACTOR_V2.md` + `AGENTS.md` | V1 prompt SUPERSEDED; V2 includes survival + architecture gauntlet |
| `schemas/checkpoint.schema.json` | `schemas/survival-checkpoint.v2.schema.json` | old unversioned contract MUST NOT coexist as authority |
| `schemas/project_state.schema.json` | `schemas/survival-project-state.v2.schema.json` | old unversioned contract MUST NOT coexist as authority |
| `templates/HANDOFF.md` | V2 `templates/HANDOFF.md` + root `HANDOFF.md` | V2 compatible superset |

## Migration law
- Never delete PR #2 history to make V2 appear original.
- Do not load V1 and V2 state/checkpoint schemas simultaneously as equivalent authority.
- A consumer referencing an old path must be migrated explicitly or stopped fail-closed.
- Current runtime implementation must use versioned V2 contract IDs after the V2 schema gate is accepted.
- PR #2 may be closed as `SUPERSEDED` only after PR #3 combined-head evidence demonstrates F1 preservation and V2 replacement coverage.

## Functional coverage added beyond V1
V2 additionally provides deterministic reference reducer/replay, freshness seal, checkpoint integrity verification, death-drill evaluator/tests, current state/task/handoff surfaces, source-of-truth matrix, architecture/assurance/recovery/security models, gap matrix, ADR, implementation checkpoints and supply-chain CI hardening.
