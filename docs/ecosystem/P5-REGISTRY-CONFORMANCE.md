# P5 Canonical Registry and Compatibility Contract

**Status:** certified for the reviewed repository/reference scope  
**Canonical schema:** TSIC `schemas/registry/v2/registry-manifest.schema.json` (vendored byte-for-byte at `schemas/registry/v2/registry-manifest.schema.json`)  
**Compatibility:** v1 remains immutable and is deprecated in the v2 registry; v2 is the active contract.  
**Registry snapshot:** `registries/ecosystem-registry.json`  
**Runtime validator:** Platform `tinlance_agent_platform_registry.ecosystem.EcosystemRegistrySnapshot`  
**CI gate:** `scripts/p5_registry_conformance.py`

**Certification evidence:** `docs/ecosystem/P5-FORENSIC-AUDIT.md` records the exact reviewed baseline, merged implementation PRs, post-merge CI/security/CodeQL/attestation runs, exact-lock integration, and negative registry/lifecycle tests. P5 is closed in the canonical phase matrix; the current active phase is P9. Pending supply-chain attestations remain explicitly deferred to P10 and are not represented as verified.

## Registry layers

- **Repository registry:** full immutable reviewed commit SHA, publisher identity and verification state, lifecycle state, provenance/SBOM/signature references, and architectural role.
- **Service registry:** unique service identity, owner repository, semantic service version, API version, required contract IDs, declared capabilities and authority mode.
- **Agent registry:** unique agent identity, owner repository, immutable reviewed revision, declared capabilities, exact required contract versions and delegated-only/authority-free mode.
- **Contract registry:** immutable contract identity/version, owning repository, authoritative artifact path, lifecycle/deprecation replacement and compatibility policy.
- **Compatibility registry:** explicit consumer-to-contract supported versions. Unknown, stale, missing or incompatible entries must be rejected.

## Authority law

Platform is the only service with `sole_consequential_execution`. OS, SDK and TADL are authority-free; TSIC is conformance-only. Agent registrations can be delegated-only or authority-free and never grant execution authority. Declared capabilities are descriptive registrations; Platform policy, approval, tenant scope, budget and sandbox checks remain authoritative for each consequential action.

## Exit gate

The exact-SHA conformance gate must reject duplicate or missing IDs, unresolved owners, repository pin drift, absent contract artifacts, undeclared capabilities, unsupported contract versions, missing compatibility rules, mutable contract versions, authority-mode drift, missing publisher identity, missing provenance/SBOM/signature references, stale supply-chain SHAs, revoked publishers, and active use of quarantined/revoked/deprecated resources. Deprecation requires an active replacement. Negative tests cover stale refs, missing supply-chain references, invalid lifecycle transitions, incompatible versions and unauthorized authority claims. Supply-chain references marked `pending` are not treated as cryptographically verified; exact attestation verification remains a P10 gate.

## Production limitation

This phase certifies repository and runtime-validator behavior. It does not by itself prove a live multi-tenant registry database is deployed or populated with production registrations. Deployment, operator controls, cache invalidation and runtime registration mutation permissions remain part of P10 operational certification.
