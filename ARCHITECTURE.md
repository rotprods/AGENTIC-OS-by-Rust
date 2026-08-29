# ROT Agentic OS — Architecture Boundary

This repository is the executable greenfield runtime for ACM vNext.

## Authority
- `rot.knowledge`: constitutional governance/change-control.
- CP01: contract semantics reference.
- CP02: canonical identity semantics.
- CP03: durable Event Ledger semantics.
- COS 2.0: event-derived graph semantics/algorithms.
- Mission Control: disposable read/proposal projection.

## Target stack
- Rust 2024: critical kernel.
- PostgreSQL: future durable production ledger/projections.
- SQLite: reference/replay backend.
- Python: GraphRAG/LangChain/LangGraph intelligence plane.
- TypeScript: query/control-plane SDK and Mission Control UI.
- GraphQL: human/product query plane.
- MCP: runtime context/tool plane.
- A2A: agent-system federation.

## Non-negotiable laws
1. No durable graph mutation without an accepted event.
2. No identity resolution by name/fuzzy similarity alone.
3. No LLM or GraphRAG inference is a fact without evidence/authority validation.
4. No projection reverse-writes authority.
5. No irreversible action from stale revision/head/horizon or active barrier.
6. All critical contracts are deterministic and parity-tested across Rust/TS/Python.

## Current boundary
Only F1 contract-kernel work is authorized on the current branch. Databases, graph port, AI plane, protocols and UI are explicitly deferred until G1 passes.
