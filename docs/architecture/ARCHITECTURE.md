# TADL Architecture

## Four planes

1. Developer plane — TADL defines and packages agent behavior.
2. Operating plane — Agent OS owns workspace, sessions, tasks, orchestration, memory, channels, fleet, and remote lifecycle.
3. Authority plane — Agent Platform owns identity, authorization, policy, approvals, runtime, tools/MCP, sandbox, secrets, budgets, evidence, audit, and observability.
4. Product/domain plane — BugFlow, FDSE Toolkit, TwinGuard, AI Shield, ThreatFade, ReconOS, TADS, FAS, Hezqara, FadeReach, and future products retain domain ownership.

## Canonical flow

Skill → Agent → Capability request → Platform authorization → Tool → Evidence

A workflow composes these steps but cannot grant authority.

## Capability equation

EffectiveCapabilities = Declared ∩ PlatformAuthorized ∩ TenantPolicy ∩ TaskScope ∩ ApprovalState ∩ EnvironmentConstraints

## Principle

Define behavior in TADL; operate it in Agent OS; authorize it in Agent Platform.
