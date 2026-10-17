# P3 — Canonical Event Delivery and Durability

**Canonical phase:** P3 in `docs/ecosystem/PHASE-MATRIX.md`  
**Status:** IN PROGRESS — forensic findings recorded; implementation and exact-SHA conformance are underway.  
**Authority boundary:** Platform owns authoritative execution/audit events and the governed outbox. OS owns workspace/task lifecycle signals and must not create a competing execution authority. SDK transports typed envelopes only. TADL declares and validates the versioned contract. TSIC certifies system-of-systems conformance.

## Forensic baseline

Reviewed source revisions at phase start:
- Platform `c094160a243382b043f40bb642f758a30e6203ff`
- OS `6a37934a2e602c6f31c2c6b943500af92d528f5b`
- SDK `8a41d6dce2fe778ab25c33dfa315328d06ec4908`
- TADL `d64a9453a1ee0b147b5f660fb53b1bce2405a714`
- TSIC `9d4361a16ae1a5570eee49d6baf499f61e222a20`

## Findings

### P3-01 — Event envelope mismatch

TSIC has an event-envelope schema, but it uses snake_case extensions such as `tenant_id`, `execution_id`, `trace_id` and `data_content_type`. The canonical CloudEvents core uses `datacontenttype`, and CloudEvents extension attribute names cannot use underscores. Platform stores only a minimal internal `Event`; OS's SQLite `EventEnvelope` lacks source, specversion, execution ID and trace ID; SDK has idempotency helpers but no typed event-envelope contract. There is no single schema/example validated by the default TADL contract suite.

**Required fix:** introduce versioned `event-envelope/v1` in TADL, use CloudEvents 1.0 core attribute names plus lowercase tenant/execution/trace/correlation/idempotency extensions, mirror the same schema in TSIC, and validate example plus adversarial cases in CI.

### P3-02 — Platform event store is volatile

Platform `InMemoryEventStore` is the only event-store implementation in the reviewed event package. Process restart loses events and event-ID deduplication state. It has no durable event store, persisted inbox, or consumer-side deduplication.

**Required fix:** implement durable reference storage and durable inbox deduplication, scoped by tenant and consumer, with stable event identity and payload-conflict detection. Do not claim exactly-once delivery; specify at-least-once delivery plus idempotent consumers.

### P3-03 — Platform outbox is not durable and leases can strand work

The current `TransactionalOutbox` is a thread-safe in-memory dictionary. Its lease has no owner or expiry, and a worker crash can leave records leased indefinitely until manual release. It lacks persisted retry scheduling, bounded backoff, terminal dead-letter state and replay audit.

**Required fix:** add a SQLite reference adapter with WAL, transaction-safe claims, owner-bound expiring leases, bounded retries/backoff, dead-letter/replay support, restart tests and deterministic behavior under duplicate publish/ack.

### P3-04 — Execution state and outbox are not atomically committed

The durable execution journal uses SQLite/WAL, while the event outbox is in memory and not part of the journal transaction. A process crash can commit execution state without its event, or publish an event without the matching durable transition.

**Required fix:** provide an explicit same-database transaction path that writes a journal transition and its outbox event atomically. Require matching database identity; reject cross-database “atomic” claims. Preserve the existing invariant that side-effect markers cannot be cleared and unknown side-effect outcomes are never blindly replayed.

### P3-05 — OS deduplication can silently accept conflicting replays

The OS SQLite runtime deduplicates by `(workspace_id, dedupe_key)`, but when a duplicate key arrives with a different event type or payload it returns the earlier event instead of reporting an idempotency conflict. Pending deliveries are listed but not leased, so concurrent workers can process the same delivery. Delivery rows do not include a lease owner/expiry or a consumer inbox key.

**Required fix:** persist a canonical envelope; compare a canonical payload digest on dedupe; reject same-key/different-content conflicts; add expiring delivery leases and inbox dedupe; test restart, concurrent claim, retry exhaustion, dead-letter and replay. Keep workspace and tenant isolation explicit and non-interchangeable.

### P3-06 — Existing retry/replay semantics are underspecified

OS has retry counts, dead-letter state and replay, but no backoff or worker lease. Replay changes delivery state without a durable replay audit and can reuse the same delivery path without a clear replay idempotency contract. Platform outbox has no dead-letter/replay model.

**Required fix:** define delivery state transitions, bounded retry schedule, lease expiry recovery, dead-letter/replay authorization, preserved event identity, replay audit and consumer idempotency. Ordering is not guaranteed unless an explicit aggregate/ordering key is configured.

## Standards and delivery semantics

- CloudEvents core 1.0.2 is the compatibility target for event envelope semantics.
- W3C Trace Context is a P4 cross-cutting propagation requirement; P3 must preserve the trace ID field without inventing or mis-parsing a W3C `traceparent`.
- Durable delivery is **at least once**. Consumers deduplicate by tenant + consumer + source + event ID and must reject the same identity with a different payload digest.
- No exactly-once guarantee is claimed across a database and external broker. The outbox ensures committed event intent survives restart; idempotent consumers and reconciliation handle redelivery.
- External broker/provider selection is deferred until throughput/isolation measurements justify it; a broker is not a substitute for the durable outbox/inbox.

References:
- CloudEvents core specification: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- OpenTelemetry context propagation: https://opentelemetry.io/docs/concepts/context-propagation/

## Serial-release exit gate

- [ ] TADL canonical schema and example validate; missing tenant/execution/trace context, invalid trace IDs and undeclared sensitive fields are rejected.
- [ ] TSIC schema and contract metadata agree with the TADL canonical schema and delivery semantics.
- [ ] Platform event envelopes preserve source, event identity, tenant, execution, trace/correlation and payload digest.
- [ ] Platform durable outbox persists across restart, uses expiring owner-bound leases, bounded retries/backoff, dead-letter and audited replay.
- [ ] Platform durable inbox deduplicates by tenant/consumer/source/event ID and rejects payload-digest conflicts.
- [ ] Execution journal transition plus outbox insertion can be committed atomically in the same SQLite transaction; cross-database atomicity is rejected.
- [ ] OS event runtime uses the canonical envelope, detects conflicting duplicate keys, recovers expired delivery leases and enforces tenant/workspace isolation.
- [ ] SDK provides typed event envelope/idempotency contract without granting authority.
- [ ] Crash/restart, concurrent lease, duplicate delivery, ack loss, database outage, retry exhaustion, dead-letter replay and cross-tenant tests pass.
- [ ] P2 regression remains green while P3 is in progress; P4–P10 remain not started.
- [ ] Four-repository lock and manifest pin exact reviewed SHAs; TSIC certification and TADL CI/security/Ecosystem Integration are green on exact head and post-merge commit.
- [ ] Post-phase forensic audit records actual evidence and remaining production limitations.

## Production boundary

A green local SQLite reference suite does not prove production PostgreSQL transactions, multi-region delivery, a broker deployment, high availability, RPO/RTO, load/capacity, backup/restore, monitoring or incident response. Those remain unverified until directly evidenced. P3 must not be certified by schema presence or in-memory unit tests alone.
