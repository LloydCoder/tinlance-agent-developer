# Canonical P10 — End-to-End Recovery and Production Certification

**Status:** In progress. P0–P9 have been certified for their exact reviewed repository/reference scope. P10 is the final ecosystem phase; it must not be confused with repository-local phase 10s or TSIC's independently numbered conformance sequence.

## Objective

Prove that the four-repository governed Agent System recovers safely from transient failures, duplicate delivery, worker interruption, provider timeout and durable-event replay, while preserving tenant isolation, Platform-only consequential authority, evidence lineage and budget correctness. Keep repository-level conformance separate from proof of a deployed production environment.

## Required recovery evidence

1. **Exact revisions:** every run validates the four-repository ecosystem.lock.json and the pinned TSIC integration authority; the manifest and lock must agree on exact 40-character SHAs.
2. **Durable execution/event path:** event delivery is idempotent; outbox publication can recover after release/retry; OS event state survives process/runtime restart; dead-letter replay is audited and tenant-scoped.
3. **Retry safety:** retries are bounded; non-retryable failures stop; consequential operations do not retry by default unless idempotency and explicit policy make retry safe.
4. **Failure injection and recovery objectives:** recovery drills declare failure mode, RTO, RPO and evidence reference; empty drill sets, missing evidence and exceeded objectives fail closed.
5. **Tenant and authority safety:** cross-tenant reads/mutations/approvals are denied; recovery, replay, memory, evidence and budgets remain tenant-scoped; OS and SDK cannot create a second authorization or ledger authority.
6. **Replica invariants:** exactly two deterministic fixture replicas use unique tenant and workspace identifiers and share the same versioned contracts. Replication fixtures contain no credentials or customer data.
7. **Cross-repository certification:** the exact-lock P10 conformance gate runs Platform recovery/durability tests, OS durable-event/replay tests, SDK retry tests, and replica/lock validation.
8. **Post-merge assurance:** all required CI, security, CodeQL, secret-scan, supply-chain, release-attestation and ecosystem workflows pass on the merged revisions and the final refreshed lock.

## Implementation and certification sequence

- Platform PR: recovery objective/failure-mode regression tests, bounded RTO/RPO behavior, required evidence reference, and failure-closed gate.
- Agent OS: prove durable event replay/restart behavior and tenant-scoped replay in the existing event runtime suite; fix any gaps surfaced by tests.
- Platform SDK: prove bounded retry and no implicit retry of consequential operations; keep retries subordinate to Platform idempotency/authority semantics.
- TADL: add scripts/p10_recovery_conformance.py, phase-specific docs and executable tests; validate exact lock/manifest and the two-replica fixture.
- TSIC: add an explicit canonical ecosystem P10 recovery contract without renumbering or redefining TSIC-00…TSIC-19.
- Merge each repository PR only after its exact-head checks are green. Refresh lock/manifest/registry to the exact merged SHAs in a final TADL certification PR, then run P10 cross-repository and post-merge gates.

## Production assurance boundary

Repository CI does not prove production TLS termination, OAuth/JWKS issuer/audience configuration, egress restrictions, live provider access, durable production database/queue configuration, real backup restoration, telemetry/alert delivery, incident response ownership or an actual failover drill in the deployed environment. These need separately captured deployment evidence with timestamps, environment identifiers, measured RTO/RPO, restore integrity results and responsible operator sign-off.

Do not set certification_state.production to certified or claim public production readiness from repository fixtures alone. If external deployment evidence is unavailable, P10 may only be described as repository-certified with production deployment explicitly unverified; it must not be advertised as 100% production-ready.

## Exit gate

- [ ] Recovery, replay, idempotency, tenant isolation and budget-settlement regressions pass.
- [ ] Recovery gate rejects missing evidence, empty drill sets and RTO/RPO overruns.
- [ ] Exact-lock four-repository and TSIC conformance passes.
- [ ] Replication fixtures validate and cross-tenant tests fail closed.
- [ ] All P10 implementation PRs merge from green exact-head CI/security checks.
- [ ] Final lock, manifest, phase matrix and certification record pin the same merged SHAs.
- [ ] Post-merge CI, Security, CodeQL, Secret Scan, Scorecard, Supply Chain Attestation, Release Attestations and Ecosystem Integration pass.
- [ ] External deployment evidence is attached and independently reviewed before claiming production certification.

## Current external blockers

External production deployment evidence has not been established by the repository workflows reviewed for this phase. Production egress, TLS/OAuth/JWKS, live provider connectivity, real backup/restore, production telemetry and incident-response drills remain unverified until supported by actual environment evidence.


## Final repository-level certification result — 2026-10-18

**Repository P10 recovery certification: PASS.** The exact-lock P10 gate passed on the reviewed implementation SHAs and pinned TSIC contract. The P10 certification PR was merged at `ca7febe109b0220a16c1c791aedfa004f016cad8`. Post-merge CI, Security, CodeQL, Secret Scan, Scorecard, Supply Chain Attestation, Release Attestations and Ecosystem Integration passed on that merge commit. The evidence covers repository-level recovery/replay, tenant isolation, bounded retries, budget settlement, and two-replica invariants.

**Production deployment certification: NOT ESTABLISHED.** External production TLS/OAuth/JWKS, egress policy, live provider access, durable production persistence, real backup/restore, telemetry/alert delivery, capacity, and incident-response drills have not been independently evidenced here. Accordingly, `certification_state.production` remains `unverified`; no claim of 100% production readiness is made. The external deployment checklist remains open until actual environment evidence and operator sign-off are supplied.
