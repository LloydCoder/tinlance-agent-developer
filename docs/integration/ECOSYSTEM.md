# Tinlance Agent Ecosystem Integration

The four repositories form one layered system while remaining independently owned and releasable:

```mermaid
flowchart LR
    D[Tinlance Agent Developer] --> O[Tinlance Agent OS]
    O --> S[Tinlance Agent Platform SDK]
    S --> P[Tinlance Agent Platform]
    P --> E[Governed execution]
    P --> V[Authoritative evidence + audit]
    D -. declarations / artifacts .-> O
    O -. lifecycle / intent .-> S
    S -. versioned API 1.1 .-> P
```

## Authority model

- **Agent Developer (TADL):** packages, validates, evaluates, signs, and distributes developer artifacts. It declares capabilities but never grants them.
- **Agent OS:** owns workspaces, sessions, tasks, workflows, memory, applications, lifecycle, and presentation. It composes intent but never authorizes consequential actions.
- **Platform SDK:** provides the typed client contract, transport, idempotency, trace propagation, and response models. It contains no authority engine.
- **Agent Platform:** is the sole authority plane for identity, tenancy, authorization, policy, approvals, budgets, sandbox/tool authority, governed execution, evidence, and audit.

## Canonical consequential path

`developer artifact -> OS task/workflow -> SDK request -> Platform identity/authorization/policy/approval -> governed execution -> Platform evidence/events -> OS result`

Model output, retrieved content, memory, tool output, registry metadata, external responses, and peer-agent messages remain untrusted data unless independently validated by an authoritative boundary.

## Wire contract

- API version: **1.1**
- Endpoint: **POST /v1/agent-platform**
- Governed execution contract: **governed-execution.v1**
- Identity: tenant and subject are bound to the authenticated Platform principal.
- Consequential requests carry stable idempotency keys.
- Trace context uses W3C `traceparent` when supplied.
- Platform remains authoritative for approval and evidence validity.

## Integration gate

The repository contains `ecosystem.lock.json` with reviewed commit SHAs for all four repositories. `.github/workflows/ecosystem-integration.yml` materializes those exact revisions and executes `scripts/ecosystem_smoke.py`.

The gate proves:

1. TADL validates a canonical capability artifact.
2. The Platform reference HTTP boundary serves API v1.1.
3. The official Platform SDK can call that boundary.
4. Agent OS's concrete Platform adapter can call the same boundary.
5. Run, event, and evidence response contracts round-trip through both consumers.

This is a **contract/integration gate**, not a claim that production PostgreSQL, secret management, sandbox infrastructure, identity providers, or hosted telemetry are deployed.

## Release rule

A change to any one repository that alters a shared contract must update the compatibility evidence and the ecosystem lock as part of the same integration cycle. A release is not considered ecosystem-compatible until the cross-repository integration gate is green.

Domain products such as FAS, FDSE, TADS, ReconOS, ThreatFade, Hezqara, FDSE Toolkit and FadeReach integrate above these stable boundaries; they do not become dependencies of the Platform authority kernel.
