# P0 — Ecosystem Forensic Baseline

**Status:** implementation baseline  
**Baseline ID:** `p0-2026-10-07`  
**Phase:** P0 — Ecosystem Forensic Baseline

## Purpose

P0 converts the four repositories from four individually mature codebases into one explicitly versioned, reviewable ecosystem release unit.

It does **not** create a fifth runtime or authority plane. The Tinlance Agent Platform remains the sole execution authority.

## Four-repository boundary

| Repository | Plane | Authority |
|---|---|---|
| `tinlance-agent-developer` | Declarative developer plane | Declares and validates intent; never grants execution authority |
| `tinlance-agent-os` | Operating/lifecycle plane | Owns workspace, task, workflow and lifecycle composition; never grants execution authority |
| `tinlance-agent-platform-sdk` | Developer API surface | Typed transport/composition only; never authorizes |
| `tinlance-agent-platform` | Authority/execution plane | Sole authority for identity, tenancy, authorization, policy, approvals, budgets, sandbox/tool authority, secrets, execution and authoritative evidence |

The immutable boundary is:

`declared capability ∩ Platform authorization = effective capability`

For consequential execution, the stronger fail-closed formulation is:

`effective authority = authenticated principal ∩ tenant ∩ registered capability ∩ policy ∩ risk constraints ∩ required approval ∩ budget ∩ sandbox ∩ secret scope ∩ execution context`

If any required control is absent or invalid, execution must fail closed.

## Release-unit artifacts

- `ecosystem.lock.json` — reviewed commit pins for the four repositories.
- `docs/ecosystem/ecosystem-manifest.json` — machine-readable ecosystem role, authority, contract and release-gate manifest.
- `scripts/validate-ecosystem-manifest.mjs` — executable consistency gate.
- `docs/integration/CONFORMANCE.md` — cross-repository executable conformance contract.

The lock is a **reviewed baseline**, not a mutable branch pointer. A new ecosystem baseline is created when reviewed revisions change.

## Mandatory gates

A P0 release baseline is valid only when:

1. all four repositories have the reviewed commit available;
2. repository CI is green;
3. security workflows applicable to each repository are green;
4. the cross-repository conformance suite is green;
5. repository roles and authority ownership are consistent;
6. all ecosystem pins are full 40-character commit SHAs;
7. Platform API and governed-execution contract versions match;
8. repository evidence is not represented as proof of external production infrastructure.

## Forensic evidence policy

A green GitHub Actions run proves the workflow's repository checks for that revision. It does not prove that a production PostgreSQL cluster, KMS/HSM, secret manager, sandbox fleet, telemetry backend, backup system, incident process or independent assessor exists outside the repositories.

External assurance remains separately evidenced.

## Standards alignment

P0 records alignment with NIST's current agent identity/authorization and interoperability work, OWASP's 2026 agentic security risks, MCP's 2026-07-28 authorization/transport changes, A2A 1.0.x enterprise authentication/discovery semantics, and OpenSSF supply-chain guidance. These sources inform the design; executable repository contracts remain authoritative.

## Exit criterion

P0 is complete only when this manifest validates, the TADL CI gate is green, the ecosystem conformance workflow is green against the reviewed baseline, and the four repositories remain within their authority boundaries.

P1 may not start before those conditions are met.
