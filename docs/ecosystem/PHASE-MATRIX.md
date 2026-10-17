# Tinlance Agent System — Finite Phase Certification Matrix

**Baseline:** ecosystem certification sequence P0–P10 / 2026-10-17

## Phase namespace and current certification state

The ecosystem P0–P10 sequence below is the release/certification sequence across TADL, Agent OS, Platform SDK, and Agent Platform. It is distinct from the **TADL internal implementation phases** documented under `docs/architecture/PHASE-0.md` through `PHASE-10.md`. The internal phase numbers describe the TADL artifact/tooling build; they are not aliases for ecosystem P0–P10. This distinction prevents the same phase number from being interpreted as the same deliverable in different sequences.

As of 2026-10-17, the evidence ledger is:

- **P0 — in progress:** lock/authority/phase-namespace reconciliation and the TSIC reference-versus-live certification boundary are being repaired and must pass the exact PR checks before P0 can be certified.
- **P1 — contract-certified, release-blocked by P0:** canonical Transformation contract evidence exists; this does not permit P2 to begin until P0 is green and merged. See `docs/ecosystem/P1-TRANSFORMATION.md` for exact reviewed SHAs and workflow evidence.
- **P2–P10 — not yet certified in this serial release sequence:** implementation artifacts or older workflow records may exist, but no phase may be advanced solely because a repository file or legacy registry says it is complete. Each phase must satisfy the gate and post-phase audit defined here.

The TSIC TSIC-00…TSIC-19 integration registry is a separate system-of-systems certification sequence. It must not be treated as the same numbering as ecosystem P0–P10. Crosswalks between the two sequences must identify exact requirement IDs and evidence rather than assuming numeric equivalence.


The manifest's `phase: "P10"` field is retained as a **contract-surface scope marker** because the validator must also validate the replication/v1 artifacts. It is not a claim that ecosystem P10 is certified. `certification_state` is the authoritative serial release ledger: while P0 is open, `sequence_release` must remain `blocked_at_p0`; only after P0 and P1 are certified may it advance to `ready_for_p2`.


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
