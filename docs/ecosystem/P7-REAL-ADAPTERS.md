# P7 — Real Adapters and Integration Boundaries

**Status: certified for the reviewed repository/reference scope.** This is canonical ecosystem P7. It is distinct from TADL's internal Phase 7, Platform's historical evaluation-safety document, and TSIC-07.

## Boundary model

- **Platform:** sole authority for identity, tenant authorization, policy, approvals, budgets, sandboxing, secret scope, route selection, and consequential execution. Provider adapters are invoked only after governed Platform decisions.
- **SDK:** typed client contract and normalized errors; no independent policy or provider credentials.
- **Agent OS:** lifecycle orchestration and Platform transport; no direct provider or tool execution that bypasses Platform.
- **TADL:** adapter contracts, validation fixtures, reproducible conformance and release evidence; no execution authority.
- **TSIC:** canonical cross-system contracts and conformance authority; not a runtime or production adapter host.

## Adapter invariants

1. Endpoints and credentials are explicit trusted configuration; never accept provider endpoints, authorization headers, retry policy, or secret references from untrusted task/model/event content.
2. Remote endpoints require HTTPS. Loopback HTTP is permitted only in explicitly enabled deterministic tests. Reject URI-embedded credentials and authenticated redirects.
3. Bound request/response sizes and timeouts; validate content types, status codes, response schemas and provider/model identity.
4. Normalize errors without exposing tokens, raw response bodies, prompts, tenant identifiers or other sensitive context in logs/exceptions.
5. Propagate trace context only through approved fields. Do not disclose internal tenant/agent identifiers to third-party providers unless a separately reviewed contract explicitly requires it.
6. Retries are operation-specific. Do not automatically retry ambiguous consequential operations or provider requests where a timeout may duplicate billed work; classify retryability for a governed caller decision.
7. The current provider adapter is synchronous and exposes a finite timeout, not an in-flight cancellation handle. A timeout or caller abandoning a wait is not proof the remote provider stopped. Do not claim remote cancellation unless a provider-specific contract and evidence establish it.
8. Adapter metadata and provider responses never grant identity, capability, approval, budget, sandbox or execution authority.

## P7 exit gate

- [x] Platform provider-compatible adapter has deterministic endpoint tests for success, malformed payloads, error normalization, timeouts/size bounds, redirects, credentials and trace validation.
- [x] SDK and OS client/transport contracts have tests for API-version compatibility, idempotency, trace propagation, finite timeout behavior and normalized errors; unsupported in-flight/remote cancellation is explicitly documented and never claimed.
- [x] Cross-repository conformance tests use exact immutable repository SHAs and deterministic endpoints; positive and adversarial paths cover tenant spoofing and authority-shaped metadata.
- [x] TSIC schema/contract and adapter conformance requirements are versioned and validated.
- [x] All relevant CI, security, static-analysis and integration workflows pass on PR heads and merge commits.
- [x] Lock, manifest, phase matrix and release notes are reconciled to exact merged SHAs.
- [x] A post-merge forensic audit records implementation evidence, workflow IDs, residual risk and external deployment limitations.

Repository tests do not prove a live provider, production credential, secret-manager integration, network egress policy, telemetry backend, quota controls or deployed infrastructure. Those remain unverified unless independently evidenced. Production egress policy must constrain provider destinations at the network boundary (including DNS/IP resolution and metadata/private-network destinations) because trusted configuration alone is not a substitute for deployed SSRF controls.


## Post-merge forensic evidence

- Merged P7 implementation: a3599dcb185806a7aea07f65f170ab8c0abde7f2 in TADL.
- Exact integration references used by the post-merge gate: TADL implementation a3599dcb185806a7aea07f65f170ab8c0abde7f2; Agent OS c68eb5e2a36a6544660145b4c997747f7ba0f605; Platform SDK 2932645977ff3e352e1bb5a94dd13389b0190f54; Platform 9da7228ecafaa92f696cc6eedaeef1ee931b03d4; TSIC authority 4ab0837e0a07cf070f3101e63ba286534ba28bff. The immutable lock's developer consumer pin for this post-merge run was ed61ab9df0ee2e761295005b93b63e3d896f99e9; the certification PR refreshes that consumer pin to the merged implementation SHA and reruns the gate.
- PR-head cross-repository integration run: 39112165212 (passed); PR-head CI 39112165141, security 39112165202, secret scan 39112165150, and CodeQL 39112165206 (all passed).
- Post-merge integration run: 39112286645, job 117630784409 (passed, including canonical P2, P3, P4, P5, P6 and P7 gates). Post-merge CI 39112286647, security 39112286650, secret scan 39112286632, CodeQL 39112286692, Scorecard 39112286657, release attestations 39112286668, and supply-chain attestation 39112286691 all passed.
- Platform adapter hardening merged at 9da7228ecafaa92f696cc6eedaeef1ee931b03d4; its PR-head CI, Reference Agents, R10, CodeQL and secret scan workflows passed. Tests cover finite positive timeouts, bounded integer response limits, sanitized timeout errors, redirect rejection, HTTPS, traceparent validation, execution-scoped credential matching, tenant/agent payload minimization and malformed/oversized provider responses.

## Residual risk and production boundary

This certification is repository-level evidence, not production certification. No live external provider credentials or billable production calls were used. Secret-manager integration, live provider behavior, deployment network egress policy, DNS/IP destination enforcement, metadata/private-network blocking, production telemetry, quotas and deployed infrastructure remain unverified. Production egress controls must constrain provider destinations at the network boundary; trusted configuration alone does not prove SSRF resistance. The synchronous adapter's finite timeout does not prove remote cancellation.

## External technical references

- [W3C Trace Context](https://www.w3.org/TR/trace-context/): validates the traceparent fields and non-zero trace/span identifiers.
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html): informs the documented requirement for destination enforcement at the network boundary.
