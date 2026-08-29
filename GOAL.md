# ROT Agentic OS — Goal

## North Star
Given only a ProjectID, ObjectiveID, AgentID, RepositoryID or ConversationID, any authorized cold runtime can reconstruct the same bounded state, event horizon, ownership, evidence, barriers, graph context and next safe action without hidden chat memory or Mission Control as sole authority.

## Current milestone
`F1_VNEXT_CONTRACT_KERNEL`

Build the smallest authoritative semantic kernel required by all later layers:
- canonical serialization;
- hashing;
- stable typed identifiers;
- temporal primitives;
- provenance primitives;
- event envelopes;
- generated/parity-friendly contracts.

## Definition of done for G1
- Rust↔TypeScript↔Python canonical byte parity: 100%;
- SHA-256 parity: 100%;
- schema accept/reject parity: 100%;
- critical line/branch/function coverage: 100%;
- changed-line coverage: 100%;
- critical mutation kill: 100%;
- requirement traceability: 100%;
- secret leakage: 0;
- tenant/scope leakage: 0;
- nondeterministic golden divergence: 0;
- P0/P1: 0.
