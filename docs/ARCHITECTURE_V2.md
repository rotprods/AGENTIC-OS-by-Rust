# ROT Agentic OS — Agent Survival Architecture V2

## Executive architecture

```text
UNTRUSTED/EPHEMERAL INPUTS
(chat, issues, provider payloads, local state)
                |
                v
        Contract Validation
                |
                v
      Accepted Event Semantics
                |
     +----------+-----------+----------------+
     |          |           |                |
     v          v           v                v
Canonical   Decision     Evidence        Coordination
Reducer     Ledger       Ledger          Claims/Barriers
     |          |           |                |
     +----------+-----------+----------------+
                |
                v
        Canonical State Snapshot
                |
        +-------+--------+
        |                |
        v                v
 COS 20D projections   ContextPack cache
        |                |
        +-------+--------+
                v
       Zero-context successor
```

## V1 → V2 delta
- V1 Survival documents were created directly on `main`, parallel to the actual F1 contract kernel. V2 is stacked on the exact verified F1 head.
- V1 described continuity mostly as policy. V2 requires executable reference contracts, reducer/replay semantics, schema tests and death-drill evidence.
- V1 listed COS dimensions. V2 treats COS as typed rebuildable projections over one event/state model with explicit NOT_APPLICABLE dimensions.
- V1 checkpoints/handoffs were templates. V2 makes freshness, parent checkpoint, event horizon, authority and evidence bindings testable invariants.
- V1 did not define a measurable architecture-refactor program. V2 compiles the program into checkpoints/tasks/DoDs and machine-readable current state.

## Source-of-truth matrix
| Concept | Authority | Projection/cache |
|---|---|---|
| identity | CP02 + executable contracts | labels/search indexes |
| accepted transitions | CP03/event contracts | issue comments, views |
| current state | deterministic reducer output | Markdown summaries |
| code | Git commit/tree | docs snippets |
| decisions | accepted ADR + supersession | summaries |
| tests/evidence | revision-pinned run/artifact evidence | dashboards |
| graph | accepted events/state + COS semantics | rendered graph/GraphRAG |
| agent context | durable state + bounded query | ContextPack/chat |

Any concept with two uncoordinated authorities is a P0 architecture defect.

## Core components
1. Contract Kernel (existing F1): canonical JSON, IDs, temporal/provenance/event envelopes.
2. Survival Contract Layer: checkpoint/project-state/handoff/context contracts.
3. State Reducer: deterministic accepted-event → canonical-state fold.
4. Coordination Kernel: claims, barriers, freshness and future leases/fencing.
5. Evidence Ledger: test/artifact/run/provenance bindings.
6. Decision Ledger: immutable decisions + SUPERSEDES edges.
7. COS Projection Adapter: one-way state/event → graph snapshots.
8. Context Compiler: bounded graph/state neighborhood + source revision seal.
9. Recovery CLI/Harness: cold reconstruction + death drill.
10. Assurance Gate: schemas, parity, replay, graph hash, recovery and security tests.

## Security model
Trust boundaries: external providers/web/issues/comments/media; repository input from untrusted branches; generated ContextPacks; LLM outputs. Treat all as UNTRUSTED_DATA until validated. Never persist secrets/PII in events, graphs, fixtures or prompts. Reject path traversal, URL/shell injection and authority self-promotion. Irreversible actions require fresh source head, event horizon, barrier/claim reconciliation and rollback path.

## Failure model
Explicitly model duplicate/out-of-order events, stale writers, partial writes, agent crash, context loss, wrong branch, projection deletion, event replay, conflicting evidence, provider timeout-after-acceptance, stale CI and graph/cache loss. Recovery is from authority, never from chat.

## Cost/performance model
Primary measured SLO: zero-context recovery <=5 minutes and <=1 bounded ContextPack. Avoid infrastructure until contention/latency/availability measurements justify it. Optimize onboarding/reconstruction cost before distributed infrastructure.

## Production bar
No Survival V2 production authority until deterministic replay, cross-language contract parity, COS rebuild parity, checkpoint recovery, concurrent claim correctness, ContextPack invalidation and synthetic death-drill SLO have exact-head evidence.
