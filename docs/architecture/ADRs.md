# Architecture Decision Records

## ADR-0001 — TADL is not a runtime
TADL defines and compiles developer artifacts; Agent OS executes lifecycle/orchestration and Agent Platform governs authority.

## ADR-0002 — Capabilities are contracts
A capability is a typed, versioned, risk-classified request surface. Skills cannot grant capabilities.

## ADR-0003 — Harnesses are untrusted
Adapters translate canonical artifacts to external harnesses. They cannot elevate authorization or alter Platform policy.

## ADR-0004 — Published artifacts are immutable
Published versions are content-addressed and cannot be silently replaced.

## ADR-0005 — Evidence authority stays in Platform
TADL declares evidence requirements; authoritative evidence is produced and governed by Agent Platform.
