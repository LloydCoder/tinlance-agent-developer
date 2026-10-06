# Tinlance Agent Developer Layer (TADL)

The canonical Tinlance developer plane for building, packaging, evaluating, versioning, signing, and distributing governed AI agents.

## Architecture

```
Developer / Product
        |
        v
TADL: skills, capabilities, agents, workflows, harnesses, evaluation, registry, provenance
        |
        v
Tinlance Agent OS: workspace, sessions, tasks, orchestration, memory, channels, fleet
        |
        v
Tinlance Agent Platform SDK: programmatic Platform surface
        |
        v
Tinlance Agent Platform: identity, authorization, policy, approvals, runtime, tools/MCP,
sandbox, secrets, budgets, evidence, audit, observability
```

## Immutable laws

- TADL defines behavior; it does not grant execution authority.
- Agent OS manages lifecycle/orchestration; it does not become the authority plane.
- Agent Platform owns governed execution and authorization.
- Harness adapters are untrusted.
- Skills cannot authorize tools.
- Learning cannot modify authority.
- Domain products retain their domain ownership.

## Product integration

BugFlow, FDSE Toolkit, TwinGuard, AI Shield, ThreatFade, ReconOS, TADS, FAS, Hezqara, FadeReach, and future products consume TADL contracts without being absorbed into this repository.

## Phase 0

Phase 0 establishes the complete repository topology, architecture decision records, ownership/boundary contracts, JSON Schema 2020-12 foundations, security policy, contribution policy, examples, test scaffolding, and CI gates.

See:
- docs/architecture/ARCHITECTURE.md
- docs/architecture/BOUNDARIES.md
- docs/architecture/ADRs.md
- docs/architecture/LIFECYCLE.md

## Local verification

```bash
npm install
npm run ci
```

Phase 0 intentionally contains no production execution runtime.
