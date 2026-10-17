# P2 — Identity, Tenancy, Authentication and Authorization

**Canonical phase:** P2 in `docs/ecosystem/PHASE-MATRIX.md`  
**Status:** CERTIFIED — reviewed repository/reference scope only; external production readiness remains unverified.  
**Authority owner:** Agent Platform. OS, SDK and TADL are consumers and may not create a second authorization authority.

## Scope

P2 establishes a concrete, testable identity path from a signed access token to a Platform principal and enforces tenant binding before any operation reaches the authority kernel:

`trusted issuer/JWKS → signature and claim verification → revocation check → normalized Principal → request tenant/subject binding → Platform authorization`

A valid authenticated principal is not itself authorization. Policy, registered capability, risk, required approval, budget, sandbox, secret scope and execution context remain independent fail-closed controls.

## Required controls

- HTTPS issuer and JWKS URLs; explicit algorithm allowlist; issuer and audience validation; access-token type and key identifier checks.
- Required and normalized `iss`, `sub`, `aud`, `exp`, `iat`, `jti`, client identity and configured principal type.
- Bounded JWKS retrieval timeout and bounded clock leeway; malformed timestamps and claims fail closed.
- Tenant identity is mandatory. If multiple configured tenant aliases are supplied, they must agree exactly.
- Roles and scopes are normalized and contradictory scope representations are rejected.
- Revocation is checked by issuer plus token identifier. A revocation-backend outage must fail closed.
- The concrete resolver maps only verified claims to the Platform Principal contract.
- Request-body tenant/subject assertions cannot override token-derived identity; cross-tenant and cross-subject attempts are denied before the handler executes.
- OS and SDK do not mint principals, widen delegated authority or bypass Platform policy.

## Executable evidence

Platform PR [#105](https://github.com/LloydCoder/tinlance-agent-platform/pull/105) is merged at `f7ed027a1db33b13594502131784105302cabc09`. It adds the concrete `JWKSPrincipalResolver`, a single-host SQLite reference revocation store, and deterministic unit plus local HTTP-boundary tests. Its pre-merge and post-merge CI, CodeQL, secret scan, R10 certification and reference-agent checks all passed on the exact PR head and merge commit. The SQLite adapter is not a production multi-instance revocation service; production must inject a shared durable backend.

The TADL phase gate adds `tests/test_identity_resolver.py` to the locked Platform regression set in addition to JWT verification, authorization enforcement and OS/SDK tenant-context tests. The phase is not certified by source-marker checks alone.

A follow-up adversarial run then found a separate object-level authorization gap: foreign-tenant `runs.events` and `runs.evidence` reads returned HTTP 200 with empty arrays. Platform PR [#106](https://github.com/LloydCoder/tinlance-agent-platform/pull/106) is merged at `c094160a243382b043f40bb642f758a30e6203ff`; it now checks run ownership before either read and denies both foreign-tenant and unknown run IDs. The P2 adversarial suite now explicitly tests both operations. The final reviewed lock pins this merge SHA; the exact-SHA adversarial and ecosystem suites pass.

Standards reviewed for this phase:
- [RFC 9068 — JWT Profile for OAuth 2.0 Access Tokens](https://www.rfc-editor.org/rfc/rfc9068.html)
- [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)

These standards inform the access-token profile; exact executable tests and the reviewed ecosystem lock determine the repository certification verdict.

## Serial-release exit gate

- [x] Platform PR #105 passed CI, CodeQL, secret scan, R10 certification and reference-agent checks on the exact head, then merged at `f7ed027a1db33b13594502131784105302cabc09`.
- [x] Platform PR #106 adds object-level tenant ownership checks to `runs.events` and `runs.evidence`, with same-tenant, foreign-tenant and unknown-run regressions; it merged at `c094160a243382b043f40bb642f758a30e6203ff` after pre-merge checks passed.
- [x] The reviewed lock pins Platform merge SHA `c094160a243382b043f40bb642f758a30e6203ff`; the P2 gate executes concrete resolver, revocation, and object-level read-authorization tests against that SHA.
- [x] Cross-tenant, cross-subject, invalid-signature, wrong issuer/audience, expiry, malformed claims, conflicting tenant aliases, and revoked-token tests pass.
- [x] Revocation-backend failure returns authentication failure and never calls the request handler.
- [x] P2 adversarial and existing governed-execution regression suites pass, including foreign-tenant `runs.events` and `runs.evidence` denial, without weakening previously certified P1 invariants.
- [x] TADL CI, CodeQL, Security, Secret Scan, Scorecard, Release Attestations and Ecosystem Integration are green on the exact candidate head and merge commit.
- [x] The four-repository lock and manifest pin full reviewed SHAs; P2 alone was `in_progress` during certification and P3–P10 remained `not_started`.
- [x] After merge, the lock and manifest were reconciled to the exact Platform merge SHA and all post-merge checks are green.
- [x] The post-phase forensic audit records exact SHAs, workflow evidence, the object-level authorization defect/remediation, and external-production limitations.

## External production boundary

Repository tests do not prove a production IdP, reachable JWKS endpoint, shared multi-instance revocation backend, key-rotation operations, production TLS/reverse proxy, monitoring, incident response, or tenant provisioning. These remain unverified until deployment evidence is inspected directly.

## Verdict

P2 is **certified for the reviewed repository/reference scope**. P3 event delivery/durability is now the next eligible phase. This certification does not claim production identity-provider deployment, shared HA revocation infrastructure, or external production readiness.


## Exact-SHA certification evidence — 2026-10-17

### Reviewed ecosystem lock

| Plane | Exact reviewed revision |
|---|---|
| TADL / developer validation | `0347f96c3f1498a178c3723111eca98de80fd6eb` |
| Agent OS / lifecycle | `6a37934a2e602c6f31c2c6b943500af92d528f5b` |
| Platform SDK / typed client | `8a41d6dce2fe778ab25c33dfa315328d06ec4908` |
| Agent Platform / authority | `c094160a243382b043f40bb642f758a30e6203ff` |
| TSIC / integration authority | `9d4361a16ae1a5570eee49d6baf499f61e222a20` |

### Platform implementation gates

- PR #105 exact-head checks: CI [39072748116](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072748116), CodeQL [39072748123](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072748123), Secret Scan [39072748182](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072748182), R10 [39072748140](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072748140), Reference Agents [39072748142](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072748142) — all passed.
- PR #105 merge SHA `f7ed027a1db33b13594502131784105302cabc09`: CI [39072823742](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072823742), CodeQL [39072823772](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072823772), Secret Scan [39072823754](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072823754), R10 [39072823777](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072823777), Reference Agents [39072823746](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39072823746) — all passed.
- PR #106 exact-head checks: CI [39073135750](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073135750), CodeQL [39073135715](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073135715), Secret Scan [39073135744](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073135744), R10 [39073135701](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073135701), Reference Agents [39073135709](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073135709) — all passed.
- PR #106 merge SHA `c094160a243382b043f40bb642f758a30e6203ff`: CI [39073213543](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073213543), CodeQL [39073213506](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073213506), Secret Scan [39073213560](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073213560), R10 [39073213490](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073213490), Reference Agents [39073213489](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39073213489) — all passed.

### Cross-repository phase gate

- TADL PR #66 exact-head checks: CI [39073444276](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073444276), CodeQL [39073444279](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073444279), Security [39073444274](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073444274), Secret Scan [39073444265](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073444265), Ecosystem Integration [39073444287](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073444287) — all passed.
- TADL merge SHA `0347f96c3f1498a178c3723111eca98de80fd6eb`: CI [39073528740](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528740), CodeQL [39073528521](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528521), Security [39073528541](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528541), Secret Scan [39073528649](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528649), Scorecard [39073528590](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528590), Release Attestations [39073528526](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528526), and Ecosystem Integration [39073528687](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39073528687) — all passed.
- The successful Ecosystem Integration run executed the TSIC authority gate, end-to-end contract smoke test, ecosystem conformance suite, governed-execution adversarial regression, canonical P2 identity/tenancy conformance, cross-cutting delegation regression and ecosystem component gate.

### Forensic verdict

The first implementation pass was insufficient: the adversarial regression uncovered a foreign-tenant object-level read-authorization gap in `runs.events` and `runs.evidence`. That blocker was fixed in PR #106, and the exact-SHA adversarial regression plus all cross-repository checks then passed. The certification is limited to reviewed source/reference behavior. Live IdP/JWKS operations, shared high-availability revocation, production TLS, monitoring, incident response and production tenant provisioning remain **unverified**.
