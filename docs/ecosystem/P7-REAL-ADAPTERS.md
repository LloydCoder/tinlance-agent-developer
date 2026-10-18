# P7 — Real Adapters and Integration Boundaries

**Status: in progress; not certified.** This is canonical ecosystem P7. It is distinct from TADL's internal Phase 7, Platform's historical evaluation-safety document, and TSIC-07.

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
7. Cancellation is best-effort unless the provider contract confirms remote cancellation. Local cancellation must not be represented as proof that a remote operation stopped.
8. Adapter metadata and provider responses never grant identity, capability, approval, budget, sandbox or execution authority.

## P7 exit gate

- [ ] Platform provider-compatible adapter has deterministic endpoint tests for success, malformed payloads, error normalization, timeouts/size bounds, redirects, credentials and trace validation.
- [ ] SDK and OS client/transport contracts have tests for API-version compatibility, idempotency, trace propagation, cancellation and normalized errors.
- [ ] Cross-repository conformance tests use exact immutable repository SHAs and deterministic endpoints; positive and adversarial paths cover tenant spoofing and authority-shaped metadata.
- [ ] TSIC schema/contract and adapter conformance requirements are versioned and validated.
- [ ] All relevant CI, security, static-analysis and integration workflows pass on PR heads and merge commits.
- [ ] Lock, manifest, phase matrix and release notes are reconciled to exact merged SHAs.
- [ ] A post-merge forensic audit records implementation evidence, workflow IDs, residual risk and external deployment limitations.

Repository tests do not prove a live provider, production credential, secret-manager integration, network egress policy, telemetry backend, quota controls or deployed infrastructure. Those remain unverified unless independently evidenced.
