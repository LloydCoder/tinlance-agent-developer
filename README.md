# Tinlance Agent Developer Layer (TADL)

TADL is the canonical Tinlance developer plane for building, packaging, evaluating, versioning, signing, and distributing governed AI agents.

## Architectural position

```
Developer / Product
        |
        v
TADL — skills, capabilities, agents, workflows, harnesses, evaluation, registry, provenance, CLI
        |
        v
Tinlance Agent OS — workspace, sessions, tasks, orchestration, memory, channels, fleet
        |
        v
Tinlance Agent Platform SDK — programmatic Platform surface
        |
        v
Tinlance Agent Platform — identity, authorization, policy, approvals, runtime, tools/MCP,
sandbox, secrets, budgets, evidence, audit, observability
```

### Immutable laws

1. TADL defines behavior; it does not grant execution authority.
2. Agent OS manages lifecycle/orchestration; it does not become the authority plane.
3. Agent Platform owns governed execution and authorization.
4. Harness adapters are untrusted.
5. Skills cannot grant capabilities.
6. Learning cannot modify authority.
7. Domain products retain domain ownership.

## Enterprise build phases

- Phase 0 — architecture foundation
- Phase 1 — canonical schemas and type system
- Phase 2 — immutable artifact registry contract
- Phase 3 — skill package system
- Phase 4 — governed capability contracts
- Phase 5 — untrusted harness adapters
- Phase 6 — agent profiles and lifecycle
- Phase 7 — workflow compiler
- Phase 8 — evaluation and certification gates
- Phase 9 — signing, provenance and supply-chain primitives
- Phase 10 — constrained learning and optimization
- Phase 11 — developer CLI
- Phase 12 — Tinlance ecosystem integration
- Phase 13 — enterprise hardening and certification readiness

## Current implementation surface

`packages/core` — canonical identifiers, risk classes, trust and integration contracts.

`packages/schemas` — schema loader, validation, and type contracts.

`packages/skills` — immutable skill package validation and dependency ordering.

`packages/capabilities` — risk-classified capability contracts and effective-capability calculation.

`packages/agents` — versioned agent profiles and lifecycle state machine.

`packages/workflows` — declarative DAG validation and compilation.

`packages/harnesses` — untrusted harness adapter boundary.

`packages/evaluation` — evaluation receipts, gates, and constrained learning proposals.

`packages/registry` — immutable artifact registry contract.

`packages/provenance` — canonical digests, Ed25519 signing/verification, and SLSA/in-toto provenance contracts.

`packages/security` — executable developer-boundary controls for authority separation and secret-like material detection.

`cli/tadl.mjs` — developer CLI validation surface.

## Ecosystem boundary

BugFlow, FDSE Toolkit, TwinGuard, AI Shield, ThreatFade, ReconOS, TADS, FAS, Hezqara, FadeReach, and future Tinlance products remain independent domain products. They consume and/or publish TADL artifacts; they are not absorbed into TADL.

## Verification

```bash
npm ci
npm run ci
npm run forensic-audit
```

CI is intentionally fail-closed: structure, schemas, lint, TypeScript compilation, runtime tests, and forensic checks must all pass. Security additionally runs dependency auditing, CodeQL, secret scanning, and CycloneDX SBOM generation. Release workflows produce signed package and SBOM attestations.

## Security posture

TADL treats skill instructions, workflow inputs, model output, memory, external documents, MCP metadata, tool output, customer repositories, and harness events as untrusted. Authority, secrets, sandbox enforcement, authoritative evidence, approvals, budgets, and audit remain in Agent Platform.

See `SECURITY.md`, `docs/security/THREAT-MODEL.md`, and `docs/security/CONTROLS.md`. Supply-chain controls are pinned to immutable action commits and release attestations use GitHub OIDC/Sigstore-backed artifact attestations.
