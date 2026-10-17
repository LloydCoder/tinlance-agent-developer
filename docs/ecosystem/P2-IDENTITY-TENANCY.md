# P2 — Identity, Tenancy, Authentication and Authorization

**Canonical phase:** P2 in `docs/ecosystem/PHASE-MATRIX.md`  
**Status:** IN PROGRESS — candidate implementation under review; not certified.  
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

The Platform candidate PR [#105](https://github.com/LloydCoder/tinlance-agent-platform/pull/105) adds the concrete `JWKSPrincipalResolver`, a single-host SQLite reference revocation store, and deterministic unit plus local HTTP-boundary tests. The SQLite adapter is not a production multi-instance revocation service; production must inject a shared durable backend.

The TADL candidate phase gate adds `tests/test_identity_resolver.py` to the locked Platform regression set in addition to JWT verification, authorization enforcement and cryptographic attestation tests. The phase is not certified by source-marker checks alone.

Standards reviewed for this phase:
- [RFC 9068 — JWT Profile for OAuth 2.0 Access Tokens](https://www.rfc-editor.org/rfc/rfc9068.html)
- [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)

These standards inform the access-token profile; exact executable tests and the reviewed ecosystem lock determine the repository certification verdict.

## Serial-release exit gate

- [ ] Platform PR #105 passes CI, CodeQL, secret scan, R10 certification and reference-agent checks on the exact head.
- [ ] Platform PR #105 is merged only after every required pre-merge check is green.
- [ ] TADL's candidate lock pins the exact candidate Platform SHA; the P2 gate executes the concrete resolver and revocation tests against that SHA.
- [ ] Cross-tenant, cross-subject, invalid-signature, wrong issuer/audience, expiry, malformed claims and revoked-token tests pass.
- [ ] Revocation-backend failure returns authentication failure and never calls the request handler.
- [ ] P2 adversarial and existing governed-execution regression suites pass without weakening previously certified P1 invariants.
- [ ] TADL CI, CodeQL, security, secret scan, supply-chain/attestation and Ecosystem Integration are green on the exact candidate head.
- [ ] The four-repository lock and manifest pin full reviewed SHAs and set only P2 to `in_progress` during certification.
- [ ] After merge, the lock is refreshed to the exact Platform merge SHA and post-merge checks are green.
- [ ] A post-phase forensic audit records the exact evidence and remaining external-production limitations.

## External production boundary

Repository tests do not prove a production IdP, reachable JWKS endpoint, shared multi-instance revocation backend, key-rotation operations, production TLS/reverse proxy, monitoring, incident response, or tenant provisioning. These remain unverified until deployment evidence is inspected directly.

## Verdict

P2 remains **not certified** until the exact Platform and ecosystem candidate revisions pass their required gates and the merged baseline is reconciled. P3 must not start before that point.
