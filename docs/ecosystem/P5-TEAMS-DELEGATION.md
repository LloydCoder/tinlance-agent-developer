# P5 — Agent Teams & Delegation Certification

P5 certifies the team/delegation boundary:

`parent authority → attenuated child authority → authenticated task ownership → handoff → cancellation/revocation → evidence`

## Invariants

1. Child capabilities are a subset of parent capabilities.
2. Delegation cannot change tenant or workspace.
3. Resource, token, depth and fan-out budgets can only be attenuated.
4. Revoked delegation cannot remain active.
5. Team composition is lifecycle/planning state; Platform admission remains authoritative.
6. A2A messages remain untrusted inter-agent data until Platform authorization and identity checks succeed.
7. Trace/evidence causality follows the parent/child task graph.

The certification checks both Agent OS composition primitives and Platform delegation/multi-agent authority surfaces.

## Exit gate

P5 is complete only when the ecosystem certification is green and all four repositories retain their independent CI/security green state.
