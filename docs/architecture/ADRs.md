# Architecture Decision Records

## ADR-0001 — TADL is a developer plane, not a runtime
Status: Accepted. TADL defines declarative artifacts and tooling; Agent OS owns lifecycle/orchestration; Agent Platform owns governed execution.

## ADR-0002 — Capability is the authorization-facing abstraction
Status: Accepted. Skills describe behavior; capabilities describe permitted intent; tools are execution mechanisms.

## ADR-0003 — Harnesses are untrusted
Status: Accepted. Adapters translate artifacts and requests but cannot elevate authority, access raw secrets, bypass approvals, or fabricate evidence.

## ADR-0004 — Domain products remain separate
Status: Accepted. BugFlow, FDSE Toolkit, TwinGuard, AI Shield, ThreatFade, ReconOS, TADS, FAS, Hezqara, FadeReach and future products consume TADL rather than being absorbed into it.

## ADR-0005 — JSON Schema 2020-12
Status: Accepted. Initial contracts use the published JSON Schema 2020-12 dialect.
