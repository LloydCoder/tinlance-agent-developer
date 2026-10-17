# P2 — Identity, Tenancy, Authentication and Authorization

**Canonical phase:** P2  
**Status:** IN PROGRESS — not certified  
**Previous gate:** P0/P1 certified for reviewed repository/reference evidence  
**Next phase:** P3 event delivery is blocked until P2 is merged, green, and post-phase audited.

## Scope and authority

Platform is the sole authority for authentication-bound principal resolution, tenant binding, authorization, policy decisions and consequential execution. Agent OS may carry tenant/subject context for a request, but may not mint or override identity. The SDK transports typed context and opaque Platform decisions; it does not authenticate a caller or grant authority. TADL packages and validates artifacts, not runtime permissions.

The effective request identity is the signed, validated identity-provider assertion bound to a configured issuer and audience. A body field, header, agent definition, memory item, tool result, registry record, MCP message or A2A message is not proof of identity.

## Forensic findings before remediation

1. The Platform HTTP boundary accepted a `PrincipalResolver` protocol, but the repository's JWT/JWKS verifier was not wired to a concrete resolver.
2. The verifier required `jti` but did not consult a revocation source.
3. Multiple configured tenant aliases could disagree without rejection.
4. The default verifier did not require a JWT access-token type, `kid`, `client_id`, or an application principal type; scope and role claim normalization was incomplete.
5. Timestamp conversion and clock-skew handling had fail-closed edge cases.
6. Existing adversarial coverage used a reference/static principal resolver. It tested forged tenant/subject and cross-tenant cancellation, but did not exercise a verified JWT through the real HTTP resolver and revocation boundary.
7. Existing OS and SDK tests carry tenant/subject context, but that transport context must never replace Platform verification.

## Required implementation and evidence

- [ ] Explicit HTTPS issuer and JWKS endpoint; no token-controlled key URLs.
- [ ] Allowlisted algorithms, access-token `typ`, `kid`, issuer, audience, expiry, issue time, subject, `jti`, `client_id`, tenant and principal type.
- [ ] Bounded JWKS timeout/cache; malformed or contradictory claims fail closed.
- [ ] Tenant aliases and `scope`/`scp` representations must agree if both are present.
- [ ] Token revocation is checked by the pair `(issuer, jti)`; a revocation backend outage fails closed.
- [ ] Verified claims are mapped into the canonical Platform `Principal` contract. OS/SDK caller-provided fields are compared against, never substituted for, that principal.
- [ ] HTTP authentication failures return 401; authenticated attempts to cross tenant/subject boundaries return 403.
- [ ] Cross-tenant read, cancel, event, evidence, approval and tool-execution tests prove no object-level authorization bypass.
- [ ] Identity, OS adapter and SDK context tests run against exact locked revisions.
- [ ] Adversarial tests cover invalid signature, issuer/audience, algorithm/type/kid, expired/not-yet-valid/future-issued token, malformed claims, tenant alias conflicts, token revocation, revocation-store outage, forged tenant/subject, and resource-ID substitution.
- [ ] CI, lint/format/type checks, security scans, secret scan, SQL isolation tests and TSIC conformance are green on exact reviewed SHAs.
- [ ] Manifest, lock, phase record and post-merge evidence are reconciled.

## Implementation record

Platform PR #105 merged at `f7ed027a1db33b13594502131784105302cabc09`. It adds a strict JWT/JWKS verifier profile, a concrete `JWKSPrincipalResolver`, a revocation-checker contract with a durable single-host SQLite reference adapter, and real local HTTP-boundary tests. The adapter fails closed when revocation status is unavailable. The SQLite adapter is not a substitute for a shared, highly available production revocation service.

P2 remains in progress until all required post-merge checks on that exact Platform commit pass, the TADL phase gate pins the merged SHA, the actual Platform/OS/SDK tests and adversarial cross-tenant reads pass, and the TADL conformance PR is merged and green.

## Standards and threat model

- RFC 9068 — JWT Profile for OAuth 2.0 Access Tokens: https://www.rfc-editor.org/rfc/rfc9068
- RFC 9700 — Best Current Practice for OAuth 2.0 Security: https://www.rfc-editor.org/rfc/rfc9700
- RFC 8725 — JSON Web Token Best Current Practices: https://www.rfc-editor.org/rfc/rfc8725
- OWASP API Security Top 10 2023, API1 Broken Object Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/

## Deployment boundary

Repository tests do not prove that a production identity provider, trusted JWKS endpoint, shared revocation database, TLS termination, key rotation monitor, token incident response, or tenant-isolated production data plane is deployed. Those remain external evidence requirements and must not be marked complete based on source code alone.

## Exit verdict

P2 remains **IN PROGRESS** until the implementation PR is merged, the canonical cross-repository gate validates exact locked SHAs, all security and CI checks pass, and the post-phase forensic audit has no unresolved identity or tenant-isolation blocker. P3 must not start before then.
