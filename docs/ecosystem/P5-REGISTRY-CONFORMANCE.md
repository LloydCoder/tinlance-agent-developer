# P5 Canonical Registry and Compatibility Contract

**Status:** in progress; not certified  
**Canonical schema:** `schemas/registry/v1/registry-manifest.schema.json`  
**Registry snapshot:** `registries/ecosystem-registry.json`  
**Runtime validator:** Platform `tinlance_agent_platform_registry.ecosystem.EcosystemRegistrySnapshot`  
**CI gate:** `scripts/p5_registry_conformance.py`

## Registry layers

- **Repository registry:** full immutable reviewed commit SHA, repository identity and architectural role.
- **Service registry:** unique service identity, owner repository, semantic service version, API version, required contract IDs, declared capabilities and authority mode.
- **Agent registry:** unique agent identity, owner repository, immutable reviewed revision, declared capabilities, exact required contract versions and delegated-only/authority-free mode.
- **Contract registry:** immutable contract identity/version, owning repository, authoritative artifact path and compatibility policy.
- **Compatibility registry:** explicit consumer-to-contract supported versions. Unknown, stale, missing or incompatible entries must be rejected.

## Authority law

Platform is the only service with `sole_consequential_execution`. OS, SDK and TADL are authority-free; TSIC is conformance-only. Agent registrations can be delegated-only or authority-free and never grant execution authority. Declared capabilities are descriptive registrations; Platform policy, approval, tenant scope, budget and sandbox checks remain authoritative for each consequential action.

## Exit gate

The exact-SHA conformance gate must reject duplicate or missing IDs, unresolved owners, repository pin drift, absent contract artifacts, undeclared capabilities, unsupported contract versions, missing compatibility rules, mutable contract versions and authority-mode drift. Negative tests are required for stale refs, missing contract declarations, incompatible versions and unauthorized authority claims.

## Production limitation

This phase certifies repository and runtime-validator behavior. It does not by itself prove a live multi-tenant registry database is deployed or populated with production registrations. Deployment, operator controls, cache invalidation and runtime registration mutation permissions remain part of P10 operational certification.
