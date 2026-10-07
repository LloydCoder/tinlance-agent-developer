# P10 — Replication & Agent System GA

P10 is the final finite ecosystem phase. It proves that the four repositories form a reusable governed Agent System rather than a single-organization implementation.

## Objective

Replicate the reference enterprise composition into two independent parameterized tenants while preserving the same contracts, workforce profile, authority boundary, evidence model, and security invariants.

This phase does **not** create a fifth runtime or authority plane.

## Replication topology

```
Reference Enterprise A ─┐
                        ├── Agent Developer → Agent OS → SDK → Agent Platform → governed world
Reference Enterprise B ─┘
```

Both replicas use the same versioned system contracts. Their tenant and workspace identities are different.

## Mandatory invariants

1. Platform remains the sole consequential authority plane.
2. Replication changes configuration/identity parameters, not authorization semantics.
3. Child/delegated authority remains attenuated by Platform policy.
4. Replica A cannot read, mutate, approve, or observe authoritative state belonging to Replica B.
5. Agent/workforce declarations remain authority-free.
6. Memory, evidence, events, traces, approvals, budgets, secrets, and execution state remain tenant-scoped.
7. No credentials, customer data, or provider-specific secrets appear in replication fixtures.
8. The same reference workforce catalog remains deterministic across replicas.
9. A replica can be upgraded or rolled back without silently changing another replica's authority.
10. Replication evidence distinguishes repository conformance from external production deployment evidence.

## Release artifacts

- `ecosystem.lock.json` — four-repository reviewed commit pins.
- `docs/ecosystem/ecosystem-manifest.json` — machine-readable ecosystem baseline.
- `docs/ecosystem/replication-manifest.json` — two-replica deterministic fixture.
- `scripts/validate-ecosystem-manifest.mjs` — executable baseline/replication gate.

## GA gate

P10 is complete only when:

- all four repository changes are merged from green PRs;
- the ecosystem manifest and lock agree on all four reviewed SHAs;
- the replication manifest validates deterministically;
- both replicas use unique tenant/workspace identities;
- cross-tenant authorization tests fail closed;
- the workforce remains authority-free;
- CI, security, CodeQL and applicable conformance workflows are green;
- documentation and release metadata identify the same P10 baseline.

P10 does not claim that an external customer deployment has been performed. A real customer replication remains an external deployment/assurance activity.

## Continuous assurance after P10

After P10, the finite build sequence ends. New work is continuous assurance: protocol evolution, vulnerability response, interoperability updates, performance/economic tuning, new reference workloads, independent assessment, and ecosystem compatibility maintenance.
