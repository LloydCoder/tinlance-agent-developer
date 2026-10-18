# Tinlance Agent System — Canonical Ecosystem Phase Matrix

**Canonical sequence:** P0–P10  
**Baseline:** ecosystem-p10-recovery-2026-10-18  
**Authority:** this matrix and `docs/ecosystem/ecosystem-manifest.json` define ecosystem phase meaning. A repository-local phase number, milestone number, TSIC number, or legacy gate filename is not an ecosystem phase.

## Phase namespace and current state

The ecosystem certification sequence is distinct from:
- TADL's internal artifact/tooling implementation phases;
- repository-specific milestones such as Platform M13/M23 or SDK M0–M11;
- TSIC's independent system-of-systems certification sequence TSIC-00…TSIC-19;
- cross-cutting capability suites such as taxonomy release, team delegation, evaluation, and reference-workforce checks.

Do not infer equivalence from matching numbers. Crosswalks must be explicit and backed by exact revision and executable evidence.

As of 2026-10-18, P0–P9 are certified for the reviewed repository/reference scope. P3 passed exact-SHA event-delivery/durability conformance; P4 passed exact-SHA trace/evidence lineage reconstruction; P5 registry v2 lifecycle and supply-chain reference governance passed exact-SHA integration and post-merge CI/security gates; P6 model/tool routing mediation passed exact-SHA Platform and TADL CI/security/integration gates; P7 real adapter and integration boundaries passed exact-SHA Platform/OS/SDK/TSIC conformance; P8 durable budget/quota/capacity/cost enforcement passed exact-SHA Platform and four-repository conformance, settlement-retry regression, post-merge CI/security/CodeQL/secret scan, Scorecard, supply-chain and release-attestation gates; P9 MCP/A2A interoperability and security passed the exact-lock four-repository/TSIC conformance gate and post-merge TADL CI, Security, CodeQL, Secret Scan, Scorecard, Supply Chain Attestation and Release Attestations on `6ec3e843622b113c23fad11e36548dabc158d5dc`. Registry v1 remains immutable/deprecated and v2 is active. P10 end-to-end recovery certification is in progress following the successful P9 closeout and post-merge gates. Production egress controls, live provider access, external TLS/OAuth/JWKS configuration, telemetry, backup/restore and deployment remain unverified until separately evidenced.

## Canonical phase sequence

| Phase | Scope | Primary ownership | Minimum exit evidence |
|---|---|---|---|
| P0 | Forensic baseline and reconciliation | TADL + TSIC, all four implementation repos | Reviewed four-repo lock; authority and phase namespace reconciled; PR inventory disposition; stale phase claims reconciled; exact-SHA CI/security/conformance evidence; explicit external-deployment limitations |
| P1 | Canonical contracts | TADL + OS + SDK + Platform | Versioned canonical schemas; lossless typed representations; contract and compatibility tests; real SDK payload validated against canonical schema; all four repos green and pinned |
| P2 | Identity, tenancy, authentication and authorization | Platform, with OS/SDK/TADL consumers | Issuer/audience/expiry/revocation checks; tenant isolation; subject and workload identity; fail-closed authorization; cross-tenant adversarial tests; no duplicate authority in OS/SDK |
| P3 | Event delivery and durability | Platform, with OS/SDK consumers | Canonical event envelope; outbox/inbox semantics; deduplication/idempotency; retries, ordering scope, dead-letter/replay and restart recovery; exact cross-repo tests |
| P4 | Trace context and evidence lineage | Platform + OS + SDK + TSIC | W3C trace context propagation; request/task/run/span correlation; evidence provenance and integrity; audit lineage; failure/retry trace tests; no invented or orphaned evidence |
| P5 | Registries and lifecycle governance | OS + Platform + TADL; SDK typed surface where applicable | Publisher/resource identity; immutable versions/digests; provenance/SBOM/signature references; compatibility; quarantine/revocation/deprecation; registry metadata cannot grant authority |
| P6 | Model/tool routing and mediation | Platform | Policy-aware route selection; capability/model/provider compatibility; budget/risk-aware decisions; fallback/retry boundaries; decision evidence; no bypass of Platform authority |
| P7 | Real adapters and integration boundaries | Platform + SDK + OS; TSIC certification | Real adapter contracts and error normalization; identity/trace propagation; timeouts, retries and cancellation; untrusted-input isolation; contract tests against real or deterministic provider-compatible endpoints |
| P8 | Budgets, quotas, capacity and cost enforcement | Platform, with OS/SDK consumers | Atomic budget reservation/settlement; tenant/org limits; concurrency and capacity caps; cancellation/refund semantics; overrun and race tests; auditable cost evidence |
| P9 | MCP/A2A interoperability and security | Platform + SDK + OS + TSIC | Authenticated protocol entry points; scoped identity and tenant propagation; Origin/SSRF protections where applicable; protocol-version compatibility; remote-agent trust; approval and tool authority enforced by Platform |
| P10 | End-to-end recovery and production certification | All four repos + TSIC | Exact-SHA system-of-systems execution; multi-tenant positive/negative paths; event, trace, evidence, registry, routing, adapter and budget integration; failure injection/restart/replay; operational and external-deployment evidence clearly separated |

## Authority invariant

`effective authority = authenticated principal ∩ tenant ∩ registered capability ∩ policy ∩ risk constraints ∩ required approval ∩ budget ∩ sandbox ∩ secret scope ∩ execution context`

Agent Platform is the sole consequential-execution and authorization authority. Agent OS owns workspace/session/task/workflow lifecycle composition. SDK transports typed contracts and opaque authoritative results. TADL declares, validates and packages artifacts. TSIC defines integration contracts and certifies conformance; it is not a runtime.

Declarations, memory, retrieved content, model output, tool output, catalog entries, registry metadata, MCP metadata, A2A messages, evaluations and transformation outcomes do not independently grant authority.

## Crosswalk for existing capability suites

Existing code contains valuable gates whose historical filenames used numbers from a different phase map. They remain useful regression suites but **do not certify the similarly numbered canonical phase**:

- Agent Catalog 20K taxonomy, semantic uniqueness and evolution controls: cross-cutting catalog release gate; not canonical P4.
- Team graph/delegation and attenuated child authority: cross-cutting delegation gate; not canonical P5.
- Platform production-runtime, evaluation-safety, enterprise-control-plane and reference-workforce suites: component-level readiness gates to be assigned as evidence to the relevant canonical phase; none alone certifies P6–P10.
- Replication manifest and deterministic replica checks: supporting P10 evidence, not production certification by themselves.
- Existing adversarial and identity scripts are regression suites. Canonical P2 is identity/tenancy; canonical P3 is event delivery; canonical P4 is trace/evidence lineage. Their gates must be explicitly wired to those scopes before the corresponding phase is certified.

The implementation may reuse existing code and tests, but the canonical phase owner must reconcile their semantics, run them against exact locked SHAs, and add any missing cross-repository integration or adversarial evidence. No phase status is inherited merely because a legacy script passes.

## Serial release rules

1. Only the first uncertified phase may be in progress.
2. A phase is complete only when its implementation, focused tests, cross-repository conformance, applicable security checks, failure/recovery evidence, documentation, lock and manifest are reconciled and merged.
3. CI must be green on the exact reviewed PR head before merge and post-merge checks must be green on the merge commit.
4. The post-phase forensic audit records actual evidence, limitations, and unresolved risks.
5. A passing repository workflow does not prove external production infrastructure is deployed. Live persistence, KMS/HSM or secret manager, sandbox fleet, telemetry, backup/restore, incident response, capacity and production identity remain unverified until directly evidenced.

## Standards watch

Use stable, versioned standards as compatibility inputs, not as authority sources:
- W3C Trace Context and OpenTelemetry context propagation for P4.
- CloudEvents semantics or a documented compatible envelope for P3, including producer-scoped event identity and duplicate detection.
- OCI distribution/artifact digest and referrer concepts as relevant to P5 supply-chain metadata.
- Current MCP Streamable HTTP and authorization specifications plus a versioned A2A release for P9. Validate `Origin`, authentication, transport security and server-side tool authorization.
- OpenSSF supply-chain controls for immutable CI dependencies, provenance and attestations.

## Current release state

P0–P8 are certified for their exact reviewed repository/reference scope. P8 post-phase audit and post-merge CI/security/CodeQL/secret-scan/Scorecard/supply-chain/release-attestation gates passed for the reviewed baseline. Canonical P9 MCP/A2A interoperability and security is `in_progress` and is not certified until Platform, OS, SDK and TADL implementation PRs merge at green exact heads, the lock/manifest/registry are reconciled to the exact merged SHAs, the P9 protocol/adversarial suites pass in both TADL and TSIC integration gates, and the post-phase forensic audit passes. P10 end-to-end recovery and production certification remains `not_started`. External production egress controls, live provider access, telemetry, backup/restore and deployed production readiness remain `unverified`.
