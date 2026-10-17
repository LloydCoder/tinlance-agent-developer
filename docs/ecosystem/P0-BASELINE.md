# P0 — Ecosystem Forensic Baseline

**Status:** CERTIFIED — canonical phase map, reviewed structural/reference baseline; external production readiness remains unverified  
**Baseline ID:** `ecosystem-p0-p1-canonical-sequence-2026-10-17`  
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

P1 may not start before those conditions are met. P1 Transformation is separately certified against its exact reviewed four-repository revisions.


## Phase sequence namespace

This P0 is the **ecosystem release baseline** and is governed by `docs/ecosystem/PHASE-MATRIX.md`. It is not the TADL-internal implementation Phase 0 documented under `docs/architecture/PHASE-0.md`. Internal TADL phase documents explicitly identify their namespace so their numbering cannot be mistaken for ecosystem P0–P10.


## P0 certification evidence — 2026-10-17

- **TSIC implementation PR #62:** merged as `9d4361a16ae1a5570eee49d6baf499f61e222a20`; all 30 checks on that exact SHA passed. [TSIC-01 reference E2E](https://github.com/LloydCoder/tinlance-system-integration/actions/runs/39063755995), [TSIC CI](https://github.com/LloydCoder/tinlance-system-integration/actions/runs/39063755897), and [final TSIC-38 forensic certification](https://github.com/LloydCoder/tinlance-system-integration/actions/runs/39063755859) are recorded in the evidence ledger.
- **Post-merge evidence PR #63:** merged as `957f52399cf6cefea8e8fa4c24bc64a06a99c966`; it pins the phase evidence ledger to the reviewed TSIC implementation SHA and exact successful workflow run IDs.
- **TADL lock/manifest PR #53:** merged as `7a85cdcc63efabf4c9b9a0b0371696131aa4a0b4`; the lock pins the reviewed TSIC implementation SHA, and the manifest now explicitly records P0/P1 certification and the serial gate to P2.
- TADL CI, Security, Secret Scan, CodeQL, Release Attestations, Scorecard and Ecosystem Integration passed on the merged TADL SHA. [Ecosystem Integration](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39063986193).
- The canonical phase matrix distinguishes ecosystem P0–P10 from TADL internal phases and TSIC-00…TSIC-19. It now defines P0 baseline/reconciliation; P1 contracts; P2 identity/tenancy; P3 events; P4 tracing/evidence; P5 registries; P6 routing; P7 adapters; P8 budgets; P9 MCP/A2A; P10 end-to-end production certification. Historical taxonomy, delegation, runtime, evaluation, control-plane, workforce and replication suites are component gates, not phase completion claims. The manifest validator fails closed if downstream phases are marked active/certified while P0 is open.
- The protected live Platform smoke workflow exists, but it has not been dispatched. Therefore live deployment, production identity, persistence, secrets, sandbox isolation, backup/restore and incident-response readiness remain **unverified** and are not included in this P0 certification.

P0 is complete for the **canonical phase-map reconciliation, repository baseline, reviewed lock, structural checks, and reference integration evidence**. P1 Transformation is already certified. The next serial phase is P2 identity/tenancy; it must pass its own implementation, adversarial, cross-repository, CI/security and forensic exit gate before P3 event delivery can start.


## Canonical phase-map reconciliation — post-merge evidence

The canonical phase-map correction merged to TADL main as `3e556bd8035ee7d1bdf4cd3bf881eb62670ac777`. The reviewed ecosystem lock and manifest pin that exact commit, which contains the approved P0–P10 mapping and the cross-cutting regression-gate distinction.

| Required workflow | Run | Result |
|---|---:|---|
| CI | [39071531691](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531691) | success |
| CodeQL | [39071531814](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531814) | success |
| Security / npm audit | [39071531764](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531764) | success |
| Secret Scan | [39071531751](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531751) | success |
| Ecosystem Integration | [39071531697](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531697) | success |
| OpenSSF Scorecard | [39071531804](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531804) | success |
| Release Attestations | [39071531609](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39071531609) | success |

The exact-commit integration run passed the canonical phase-map validator, the P1 Transformation payload/schema checks, the governed-execution adversarial regression, the canonical P2 identity/tenancy regression, the cross-cutting team-delegation regression, and the supporting component regression suites. This is repository/reference evidence only. Canonical P2 identity/tenancy has not yet been certified as an ecosystem phase; it is the next phase eligible to start.
