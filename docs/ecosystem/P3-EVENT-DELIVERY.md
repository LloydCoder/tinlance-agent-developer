# P3 — Event Delivery and Durability

**Status: certified for repository/reference conformance.** This is canonical ecosystem P3, not TADL's internal Phase 3 or TSIC-03. P4 must remain not started until this phase passes.

## Scope

P3 establishes one cross-repository event contract and failure model for Platform execution events and OS lifecycle events. It covers:

- CloudEvents 1.0 JSON envelope attributes and versioned schema.
- Tenant and workspace scope that cannot be changed by event payloads.
- Event identity and deduplication semantics.
- Transactional outbox and consumer inbox contracts.
- At-least-once delivery, bounded retries with backoff/jitter, expiring owner-bound leases, dead-lettering, explicit replay and replay audit.
- Cross-repository typed serialization, exact-SHA conformance, and failure-injection tests.

## Authority boundary

Agent Platform remains the sole identity, authorization, policy, approval, budget, sandbox, secret and consequential-execution authority. OS event runtime handles lifecycle composition only. SDK event models are typed transport contracts. TSIC owns the cross-system event contract and conformance criteria.

Event names, metadata, payloads, replay parameters, retrieved content and event handlers never grant authority. Any operator identity used for replay audit must come from authenticated upstream context; the OS local runtime is not an authorization boundary.

## Delivery guarantees

Delivery is **at-least-once**, not exactly-once. A producer must persist the domain state change, event record and outbox record in one database transaction. A consumer must commit its inbox/deduplication record and business effect atomically before acknowledgement. Deduplication uses CloudEvents `source + id`, scoped to consumer and tenant. The base outbox does not guarantee ordering; an ordering key is only metadata until an ordering-aware dispatcher enforces and tests per-aggregate sequencing. Do not claim ordered delivery from key presence alone.

A worker crash after publish but before acknowledgement can produce duplicate delivery. The contract requires duplicate-safe consumers rather than promising impossible cross-system exactly-once effects.

## Exit gate

P3 is complete only when all conditions below are satisfied:

- [x] TSIC schema follows CloudEvents 1.0 naming and rejects invalid or authority-shaped fields.
- [x] Platform event envelope, transaction-bound PostgreSQL event/outbox adapter, outbox lease metadata, and tenant-isolated inbox schema pass unit and database migration tests. The adapter must not independently commit; it must use the caller's tenant-scoped connection so domain state, event, and outbox records commit or roll back together.
- [x] OS event runtime has tenant/workspace-scoped idempotency, exclusive expiring worker leases, owner-bound acknowledgement, bounded retry/dead-letter, and audited tenant-scoped replay.
- [x] SDK typed envelope serializes all required attributes and rejects invalid timestamps, trace IDs, non-JSON values, and invalid extension metadata.
- [x] The actual SDK, Platform and OS serialized envelopes validate against the exact TSIC schema from the reviewed TSIC revision.
- [x] Cross-repository tests cover duplicate delivery, conflicting idempotency reuse, tenant isolation, lease expiry/stale acknowledgements, consumer failure, retry exhaustion, replay and restart persistence.
- [x] All component PRs pass their required CI/security workflows and are merged.
- [x] The TADL lock/manifest pin exact merged SHAs; the ecosystem integration and TSIC event-contract gates pass on that candidate.
- [x] A post-merge forensic audit records evidence, residual risk and production limitations.

## Certification evidence

The exact-SHA component gate passed after the Platform, SDK, TSIC and TADL changes were merged. The forensic evidence register, exact revisions, workflow run IDs, checks performed and residual production limitations are recorded in `P3-FORENSIC-AUDIT.md`. The certified lock uses full commit SHAs and preserves Platform as the sole consequential execution authority.

## Production limitation

Passing repository tests does not prove a production broker, PostgreSQL cluster, worker fleet, monitoring, backup/restore or live deployment exists. P3 certification is repository/reference conformance until those external systems are independently evidenced. The OS P3 runtime uses versioned `*_p3` SQLite tables because the previous local event schema did not carry authoritative tenant attribution. Existing legacy rows are intentionally not auto-assigned to tenants or replayed; any deployment with legacy rows requires a separately reviewed migration using an authoritative workspace-to-tenant mapping before those rows can be consumed.
