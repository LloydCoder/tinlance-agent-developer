# P8 — Budgets, Quotas, Capacity and Cost Enforcement

**Status: in progress.** This is canonical ecosystem P8; it is not a repository-local
phase, Platform M13 milestone, or TSIC phase with the same number.

## Authority model

Agent Platform is the only admission and consequential-execution authority.
Agent OS composes task/workflow context; SDK transports typed Platform contracts;
TADL validates artifacts and ecosystem conformance; TSIC certifies system-of-systems
contracts. None of those consumers may independently grant budget, quota, or tool
authority.

## Required guarantees

1. Tenant and optional organization limits are checked atomically under transactional
   row locks before consequential work.
2. Reservations bind tenant, organization, agent, run, action, resource, idempotency
   key and all reserved dimensions.
3. Idempotency replay with the same full intent returns the original reservation;
   a changed scope or changed amount is rejected.
4. Concurrency is an active-reservation gauge, not a cumulative consumption counter.
5. Settlement records measured tool calls, token units and cost exactly once; replay
   with identical actual usage is distinguishable from a quota overrun.
6. Overrun is recorded and surfaced explicitly; no additional work is admitted after
   the overrun decision.
7. Release/refund semantics distinguish pre-side-effect cancellation from cancellation
   after a side effect. Observed usage must be settled after a consequential side effect.
8. Cost evidence is append-only, bounded, tenant-scoped, and limited to allow-listed
   scalar metadata; secrets, prompts and arbitrary provider bodies are excluded.
9. The database transaction boundary covers reservation state and ledger evidence.
   In-memory ledgers remain reference/test implementations only.
10. Capacity checks compare throughput, p95/p99 latency and concurrency against a
    declared envelope and reject non-finite or malformed inputs.

## Implementation workstreams

- **Platform:** SQL migration, RLS, tenant/organization limits, reservation state,
  atomic stored procedures, append-only cost ledger, bounded metadata, capacity and
  race/idempotency/overrun tests.
- **SDK:** preserve the Platform response as typed, non-authoritative data; no local
  authorization or independent quota accounting.
- **OS:** surface status and evidence references without making budget decisions or
  granting execution authority.
- **TADL/TSIC:** validate the exact-SHA baseline and phase requirements; never infer
  completion from a repository-local milestone or a declaration alone.

## Exit gate

- [ ] Migration is applied and tested on supported PostgreSQL versions.
- [ ] Tenant and organization races pass concurrent PostgreSQL integration tests.
- [ ] RLS, grants, cross-tenant attacks and organization membership fail closed.
- [ ] Reservation replay, conflicting idempotency, settlement replay, overrun,
  release/refund and restart/recovery semantics are tested.
- [ ] Cost ledger is append-only and evidence fields are allow-listed.
- [ ] Capacity envelope checks reject NaN, infinity, booleans where numeric values
  are required, and invalid integer dimensions.
- [ ] OS and SDK do not duplicate Platform authority.
- [ ] Four-repository exact-SHA conformance, CI, security and post-merge audit pass.
- [ ] Documentation, manifest and lock identify the same reviewed P8 baseline.

Passing unit tests or a mocked PostgreSQL connection is not proof of production
database deployment or live multi-worker safety. P8 certification must explicitly
separate repository evidence from external deployment evidence.
