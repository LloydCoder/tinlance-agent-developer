# P8 Candidate Forensic Audit — Budgets, Quotas, Capacity and Cost

**Audit state:** candidate implementation reviewed; final certification pending exact-SHA ecosystem CI and post-merge checks.  
**Canonical phase owner:** Agent Platform.  
**Follow-up Platform candidate SHA:** `1e91e21e74b7078a707b21d9fa99cf1fcde210d9`  
**Open implementation PR:** [Platform #123](https://github.com/LloydCoder/tinlance-agent-platform/pull/123) and follow-up [Platform #127](https://github.com/LloydCoder/tinlance-agent-platform/pull/127)

## Scope and authority

P8 adds persistent, transactional quota reservations, tenant and organization limits, usage settlement, capacity gates, append-only ledger evidence and expired-reservation recovery. Platform remains the only authority for admission, settlement, and consequential execution. Agent OS and the Platform SDK must not create a second quota ledger or local authorization path.

This audit distinguishes repository evidence from live deployment. A green workflow demonstrates the checked code and test environment, not a deployed production database, runtime role grants, secret manager, telemetry, backup/restore, or incident-response readiness.

## Candidate implementation evidence

- `database/migrations/010_p8_budget_quota_ledger.sql`: tenant and organization budget limits, reservation rows, ledger facts, row-level security, serialized admission, settlement, release, bounded evidence, and append-only triggers.
- `database/migrations/011_p8_quota_reservation_recovery.sql`: bounded lease renewal, batched expiry detection using `FOR UPDATE SKIP LOCKED`, recovery-request ledger facts, and explicit no-side-effect evidence before a recovery-requested reservation can be released.
- `database/tests/006_p8_quota_ledger.sql`: replay/idempotency, conflicting settlement evidence, safe evidence, numeric validation and ledger immutability.
- `database/tests/007_p8_quota_concurrency.sql`: PostgreSQL concurrent tenant and organization admission.
- `database/tests/008_p8_quota_recovery.sql`: expiry, renewal, reconciliation, measured settlement and explicit release evidence.
- `packages/budgets/src/tinlance_agent_platform_budgets/postgres_quota.py`: transaction-bound adapter. The caller owns the transaction; the adapter does not commit or close the connection.
- `tests/test_p8_budget_quota_ledger.py`: typed input validation, cost normalization, adapter contract and regression tests.
- `docs/P8-ENTERPRISE-CONTROL-PLANE.md`: Platform authority boundary and P8 operating semantics.

## Forensic findings and remediations

### P8-F01 — Expired lease could be released before reconciliation

The first candidate allowed a generic release while a reservation's lease had expired but before the reconciler set `recovery_requested_at`. That could treat timeout as proof that no consequential side effect occurred.

**Fix:** the release procedure now rejects an expired, unreconciled reservation. The regression test attempts this path before requesting reconciliation and requires a fail-closed result.

### P8-F02 — Settlement replay ignored conflicting evidence

The first candidate considered a repeated settlement idempotent if only usage quantities matched. A second request with different evidence could receive `already_settled`, even though the evidence did not match the original ledger fact.

**Fix:** the settlement procedure now requires both usage dimensions and the immutable recorded evidence to match. A conflicting-evidence replay is explicitly tested and rejected.

### P8-F03 — Capacity failure diagnostics hid the violated envelope

A pre-existing performance-economics test expected the capacity gate to identify p95 latency, but the gate returned only a generic message.

**Fix:** capacity evaluation reports the specific exceeded dimensions (throughput, p95, p99, concurrency). The regression remains in the normal test suite.

### P8-F05 — OS/SDK consumers must preserve structured budget failures

The first exact-SHA cross-repository run exposed that the locked OS revision did not contain the newer typed Platform conflict mapping. Platform may report a structured budget/settlement failure, but an older OS transport boundary cannot preserve the authoritative error code and retryability metadata. The SDK also needs to retain run failure classification rather than collapse it into an untyped result.

**Fix:** the reviewed OS main revision `e0205a4e5a4494a34d9e480a4a0b77699bcfe953` adds `PlatformConflictError` mapping and has green CI, CodeQL and Scorecard workflows; the reviewed SDK revision `e54256ce7e632ee2efe0e0a49f0e37142fe4c27c` has green CI/Security and preserves structured failure codes. The lock, manifest and registry now pin these exact revisions, and the P8 conformance gate asserts the error semantics as well as the no-duplicate-ledger boundary.

### P8-F04 — CI surfaced type, formatting and mock-contract defects

The candidate's first checks exposed Ruff formatting, a mypy variable-name collision, a stale ledger permission assertion, and incomplete adapter test doubles for lease-renewal and reconciliation return values.

**Fixes:** source formatting and typing were corrected; tests now assert the full UPDATE/DELETE/TRUNCATE revocation and model the actual datetime/count return contracts. The initial P8 implementation merged at `f1724f68715d18932b37cf07ac23843291237eaf`; follow-up PR #127 repairs the cross-repository tenancy/approval documentation markers and SDK reference-agent pin identified by the TADL exact-SHA gate. The follow-up candidate must pass the complete workflow set, then TADL must rerun conformance against its exact merge SHA.

## Security and correctness review

- Tenant and organization budget rows are locked in a consistent order during admission. SQL concurrency tests use separate PostgreSQL connections rather than relying only on in-process locks.
- Reserved capacity remains charged while a lease is expired and awaiting reconciliation. Expiry is a recovery signal, not proof of a missing side effect.
- Settlement records measured usage even when limits are exceeded, marks the result as an overrun, and requires the caller to stop subsequent work.
- Reservation retries preserve idempotency across terminal states; conflicting intent must fail closed.
- Evidence is metadata-only, size-bounded and allow-listed. Raw prompts, credentials and provider payloads are not intended to enter the ledger.
- The ledger has update/delete triggers and a truncate trigger in addition to privilege revocation.
- SQL functions use `SECURITY INVOKER`, so caller identity and row policies remain relevant; production roles must have only the required privileges and must not bypass row-level security.
- OS and SDK remain consumers of Platform-owned authority. The new TADL P8 gate checks the exact lock and rejects direct quota-table/procedure duplication in their source trees.

## External standards reviewed

- PostgreSQL row security documentation explains that RLS adds row filtering to SQL privileges, defaults to deny when no policy applies, and does not govern operations such as TRUNCATE. The candidate therefore combines tenant policies with separate ledger immutability controls: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- PostgreSQL privilege documentation explains that object privileges remain separate from RLS and that function execution privileges are granted to PUBLIC by default unless revoked. The migration revokes public execution for the quota procedures; production role-specific grants must be configured and verified: https://www.postgresql.org/docs/current/ddl-priv.html
- PostgreSQL function documentation describes SECURITY INVOKER as executing with caller privileges, which matches the intended RLS boundary: https://www.postgresql.org/docs/current/sql-createfunction.html

## Required certification gates

- [ ] Platform #123 post-merge workflows and follow-up PR #127 pass CI (Python 3.12/3.13/3.14, PostgreSQL migration/integration tests, TSIC conformance), CodeQL, Secret Scan, Reference Agents and R10 Certification on the exact reviewed head.
- [ ] TADL's P8 conformance workflow validates the exact locked Platform candidate, runs P8 adapter tests and verifies OS/SDK do not duplicate persistence or authority.
- [ ] Platform #123 is merged only after the above gates pass.
- [ ] The TADL lock is refreshed to the exact Platform merge SHA; P8 integration is rerun against that immutable merge SHA.
- [ ] Post-merge Platform and TADL workflows pass.
- [ ] P8 docs, manifest, lock, change log and post-phase forensic audit agree on the exact certified baseline.
- [ ] P9 remains not started until P8 is certified.

## Residual risks not certified by repository CI

1. Production PostgreSQL role creation, least-privilege grants, connection-pool tenant context setup, and proof that runtime roles cannot bypass RLS are deployment concerns requiring environment-specific evidence.
2. Real backup/restore, failover, load under production-scale concurrency, metrics/alerts, cost reconciliation against provider invoices, and operational incident drills remain external deployment evidence.
3. No claim is made that this repository currently has a live production quota database or that all infrastructure has been deployed.

## Verdict

The candidate closes two material correctness gaps discovered during this audit: premature release of expired work and evidence-mismatched settlement replay. P8 is not certified until the exact-SHA cross-repository gate, all required Platform workflows, merge, and post-merge verification are complete.
