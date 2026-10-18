# P7 Post-Merge Forensic Audit — 2026-10-18

## Decision

**P7 passes repository-level certification for the exact reviewed references.** This audit does not assert live provider readiness or production deployment certification. The canonical phase sequence is serial: P8 may begin after this certification change is merged with its required workflows green.

## Scope and authority boundaries

- Platform is the only authority for identity, tenancy, authorization, policy, approvals, budget, sandbox, secret scope, routing and consequential execution.
- SDK transports typed requests/results and validates trace context; it does not authorize.
- Agent OS orchestrates lifecycle and transports requests to Platform; it does not bypass Platform.
- TADL validates artifacts/contracts and assembles reproducible conformance evidence; it does not execute.
- TSIC owns canonical cross-system conformance contracts and certification authority; it is not a runtime adapter host.

## Exact reviewed references

| Component | SHA | Reviewed evidence |
|---|---|---|
| TADL implementation | a3599dcb185806a7aea07f65f170ab8c0abde7f2 | PR #78 merged; PR-head and post-merge gates passed |
| Agent OS | 7b96a860b71f717c96bdd4b27af71576e27f0739 | Traceparent propagation/validation and transport regression tests |
| Platform SDK | 4b973bec1d6cbb2420b6510ea85f130af5a44bea | Traceparent validation and typed-client tests |
| Platform | 9da7228ecafaa92f696cc6eedaeef1ee931b03d4 | Bounded OpenAI-compatible adapter, execution-scoped credentials, finite timeout/size limits and adapter tests |
| TSIC authority | 4ab0837e0a07cf070f3101e63ba286534ba28bff | Versioned provider-adapter contract/schema and conformance tests |

The certification PR updates the lock/manifest/registry developer consumer pin to the merged TADL implementation SHA and reruns the full integration gate. The lock remains immutable and every entry remains a full SHA.

## Implementation evidence

1. **Platform adapter:** packages/models/src/tinlance_agent_platform_models/openai_compatible.py enforces HTTPS except explicitly allowed loopback tests, rejects URI credentials/fragments and redirects, bounds serialized request and response bytes, uses finite positive timeouts, validates content type and provider/model response, propagates only validated W3C traceparent, classifies retryability without automatically retrying, and sanitizes transport/provider failures.
2. **Scoped credentials:** packages/secrets/src/tinlance_agent_platform_secrets/model_provider.py binds credential retrieval to tenant, principal, agent, execution and capability scope through the Platform secret broker; mismatch and missing context fail closed.
3. **OS transport:** src/tinlance_agent_os/transport.py validates and propagates a full W3C traceparent; it does not substitute a bare trace ID.
4. **SDK:** src/tinlance_agent_platform_sdk/client.py rejects unsupported traceparent versions and malformed trace context.
5. **TSIC contract:** contracts/models/provider-adapter-boundary.json, its schema, rules and tests establish Platform authority, trusted endpoint configuration, transport bounds, privacy and credential non-persistence.
6. **Cross-repository gate:** scripts/p7_adapter_conformance.py verifies immutable repository heads and runs Platform, OS, SDK and TSIC regression subsets. The run also executes the canonical P2–P6 gates and the supporting component regression suite.

## Workflow evidence

- PR-head P7 integration: run 39112165212, job 117630431525 — passed, including “Canonical P7 adapter conformance PASSED for exact locked SHAs.”
- PR-head CI: 39112165141 — passed.
- PR-head Security: 39112165202 — passed.
- PR-head Secret Scan: 39112165150 — passed.
- PR-head CodeQL: 39112165206 — passed.
- Post-merge P7 integration: run 39112286645, job 117630784409 — passed; the exact-SHA P7 conformance step passed.
- Post-merge CI: 39112286647 — passed.
- Post-merge Security: 39112286650 — passed.
- Post-merge Secret Scan: 39112286632 — passed.
- Post-merge CodeQL: 39112286692 — passed.
- Post-merge Scorecard: 39112286657 — passed.
- Post-merge Release Attestations: 39112286668 — passed.
- Post-merge Supply Chain Attestation: 39112286691 — passed.
- Platform provider-timeout hardening PR #120: merged at 9da7228ecafaa92f696cc6eedaeef1ee931b03d4; CI, Reference Agents, R10, CodeQL and Secret Scan passed. Platform reference-agent SDK pin correction PR #119 also merged with all required workflows green.
- Agent OS PR #139 and TSIC PR #75 are merged with their recorded PR-head CI/certification checks green. No open PRs remained across Platform, SDK, OS, TADL or TSIC after the P7 implementation PRs were resolved.

## Gaps closed during this phase

- Corrected stale lock/manifest/registry reviewed SHAs and baseline ID drift.
- Corrected the Platform reference-agent SDK pin so the P10 package-pin regression gate matches the locked SDK revision.
- Added explicit finite-timeout and response-limit validation and deterministic timeout tests; fixed the lint findings those tests exposed.
- Added a cross-repository P7 gate instead of relying on Platform/TSIC-only markers.
- Preserved the P10 manifest phase as a contract-surface marker while recording serial P0–P10 certification state separately.
- Documented the current synchronous cancellation limitation and production egress/SSRF requirements rather than claiming unsupported guarantees.

## Residual risks and non-claims

- No live external provider credentials or billable production requests were used.
- Secret-manager integration in a deployed environment is not proven by the deterministic scoped-secret test fixture.
- Production network egress policy, DNS/IP resolution enforcement, metadata/private-network destination blocking and DNS-rebinding defenses are not proven by repository CI.
- Production telemetry backend, operational quotas, capacity/cost controls, deployed infrastructure and disaster recovery are not certified by P7.
- The synchronous adapter exposes finite timeout behavior but no in-flight cancellation handle; a local timeout does not prove the remote provider stopped.
- W3C Trace Context and OWASP SSRF guidance informed the boundary review: https://www.w3.org/TR/trace-context/ and https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html.

## Final phase disposition

P7 is certified for the reviewed exact-SHA repository scope. Production remains unverified. P8 is the next eligible phase; P8–P10 are not yet certified.
