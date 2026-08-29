# F1 Bootstrap + Contract Convergence Evidence — 2026-08-29

Status: `INTERNAL PASS / G1 NO_GO / SHADOW_ONLY`

## Repository

- repository: `rotprods/AGENTIC-OS-by-Rust`
- base `main`: `4964721c48f62cefe5593837fed7dacfd1945253`
- branch: `feat/f1-contract-kernel-vnext`
- review surface: PR #1
- exact verified implementation head: `a0ec03ec923e2787da58dea5c3a5eedfaaefac49`

## Exact-head CI evidence

### F1 Rust Contract Kernel

Workflow run: `33266201914`

PASS:

- `cargo fmt --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --all-targets`

### F1 Cross-Language Parity

Workflow run: `33266201915`

PASS:

- Python canonical golden parity
- TypeScript strict compilation
- TypeScript canonical golden parity

## Architectural corrections made before downstream consumers exist

1. Replaced the initial UUIDv7 canonical-entity placeholder with the CP02 digest-ID family:
   - `rot:entity:sha256:<64hex>`
   - `rot:source:sha256:<64hex>`
   - `rot:revision:sha256:<64hex>`
2. Kept UUIDv7 only for execution/event-style runtime identities where the current contract permits it.
3. Added provider/account/workspace/resource/external-ID SourceIdentityKey normalization with NFC, case-sensitivity and fail-closed token rules derived from CP02.
4. Added deterministic SourceRecord and CanonicalEntity ID derivation domains matching CP02 architecture.
5. Added deterministic IdentityDecision ID derivation without moving decision-validity ownership out of CP02.
6. Replaced unrestricted floating confidence with a finite `[0,1]` value type.
7. Replaced heuristic timestamp checking with RFC3339 parsing and instant-aware validity-window checks.
8. Established CP01-derived Rust/TypeScript/Python canonical JSON/hash baseline vectors.

## Authority boundary

This evidence does not promote G1 or any runtime authority. `rot.knowledge` remains constitutional governance; CP02 remains identity semantic owner; CP03 remains durable Event Ledger owner; COS remains graph semantic/algorithm source.

## Remaining G1 blockers

- extended ECMAScript numeric canonicalization parity;
- UTF-16 key-order adversarial parity;
- full CP02 identity golden parity across all three languages;
- CP03 EventStream/Append/StoredEvent/Receipt contract parity;
- JSON Schema accept/reject parity;
- 100% critical coverage + changed-line coverage certification;
- 100% critical mutation kill;
- property/fuzz/adversarial campaigns;
- secret and tenant/scope leakage certification;
- immutable SHA pinning of CI actions;
- explicit repository visibility policy decision (repository is currently public).

No PostgreSQL, Event Ledger backend, COS2 port, GraphRAG, LangGraph, GraphQL, MCP/A2A, provider writes or Mission Control UI may start on the canonical branch before G1 PASS.
