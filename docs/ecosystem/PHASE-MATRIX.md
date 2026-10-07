# Tinlance Agent System — Finite Phase Certification Matrix

**Baseline:** P10 / 2026-10-07

This matrix is the ecosystem-level release map for the four repositories. A
phase is not considered ecosystem-complete merely because one repository says
it is complete: the phase must have an owner, executable evidence, and a
cross-repository gate where the phase crosses repository boundaries.

| Phase | Primary owner | Scope | Cross-repo gate |
|---|---|---|---|
| P0 | TADL | Four-repository lock, manifest, authority boundary | `validate-ecosystem-manifest.mjs` + ecosystem workflow |
| P1 | TADL + all four | Transformation contract from declaration to outcome | `ecosystem_phase_conformance.py` |
| P2 | TADL + Platform | Governed execution and adversarial boundary | `p2_adversarial_conformance.py` |
| P3 | Platform | Agent identity and authority | `p3_identity_authority_conformance.py` |
| P4 | Agent OS | 20K-scale canonical taxonomy gate and continuous evolution | `ecosystem_phase_conformance.py` + OS catalog tests |
| P5 | OS + Platform | Attenuated teams and delegation | `p5_team_delegation_conformance.py` |
| P6 | Platform | Production-runtime readiness contract | `ecosystem_phase_conformance.py` + runtime tests |
| P7 | Platform | Continuous evaluation and safety gates | `ecosystem_phase_conformance.py` + evaluation/security tests |
| P8 | Platform | Enterprise control plane | `ecosystem_phase_conformance.py` + control-plane tests |
| P9 | Platform | Reference enterprise workforce | `ecosystem_phase_conformance.py` + workforce tests |
| P10 | TADL + all four | Parameterized replication and Agent System GA | `ecosystem_phase_conformance.py` + replication manifest |

## Completion semantics

The finite sequence ends at P10. After P10, new work enters continuous
assurance: protocol updates, vulnerability response, interoperability,
performance/economic tuning, new reference workloads, independent assessment,
and compatibility maintenance.

A green repository workflow proves the checks executed by that workflow. It
does not prove that external PostgreSQL, KMS/HSM, secret-management,
sandbox, telemetry, backup/restore, incident-response, or independent
assessment infrastructure exists outside the repositories.

## Authority invariant

`effective authority = authenticated principal ∩ tenant ∩ registered capability
∩ policy ∩ risk constraints ∩ required approval ∩ budget ∩ sandbox ∩ secret
scope ∩ execution context`

Descriptive declarations, memory, retrieved data, catalog entries, model
output, tool output, MCP metadata, A2A messages, evaluations, attestations,
and transformation outcomes do not independently grant authority.

## Standards watch

The design is maintained against the current NIST agent identity/authorization
work, OWASP Top 10 for Agentic Applications 2026, MCP 2026-07-28, and A2A 1.0.x.
Protocol versions are compatibility inputs, not authority sources.
