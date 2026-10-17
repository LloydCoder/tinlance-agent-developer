# P2 Final Forensic Audit — Identity, Tenancy, Authentication and Authorization

**Audit date:** 2026-10-17  
**Canonical phase:** P2  
**Verdict:** CERTIFIED for the reviewed repository/reference scope. External production readiness remains unverified.  
**Authority law:** Platform remains the sole authority for authenticated identity, tenant binding, authorization, policy, approval, budget, sandbox/tool access, secrets, execution and authoritative evidence. OS, SDK and TADL are non-authoritative consumers.

## Scope and method

This audit reconciles the canonical P0–P10 phase matrix, the reviewed ecosystem lock/manifest, the P2 implementation and tests across Platform, OS, SDK and TADL, TSIC's integration authority gate, pre-merge and post-merge GitHub Actions evidence, and the cross-cutting adversarial regression. Every implementation claim below is tied to a reviewed commit and an executable gate. Repository CI is not treated as proof of external production deployment.

## Reviewed revisions

| Repository | Reviewed revision | Role |
|---|---|---|
| `tinlance-agent-developer` | `0347f96c3f1498a178c3723111eca98de80fd6eb` | Canonical phase, lock/manifest and conformance gate |
| `tinlance-agent-os` | `6a37934a2e602c6f31c2c6b943500af92d528f5b` | Tenant/subject context transport; no authority |
| `tinlance-agent-platform-sdk` | `8a41d6dce2fe778ab25c33dfa315328d06ec4908` | Typed request context; no authority |
| `tinlance-agent-platform` | `c094160a243382b043f40bb642f758a30e6203ff` | Sole identity and authorization authority |
| `tinlance-system-integration` | `9d4361a16ae1a5570eee49d6baf499f61e222a20` | TSIC integration/certification authority |

The P2 lock uses full immutable SHAs, not moving branch names. The manifest preserves `phase: P10` as a replication/v1 contract-surface marker; it is not a phase-completion field. Canonical certification state is tracked separately.

## Findings and remediation

### P2-01 — No concrete JWT/JWKS-to-principal path

**Finding:** The HTTP API accepted a resolver protocol, but the repository did not provide a concrete verifier-to-Platform-principal path.

**Remediation:** Platform PR #105 added strict JWT/JWKS verification, issuer/audience/type/key checks, normalized claims, bounded timeouts/leeway and a concrete `JWKSPrincipalResolver`. Verified claims are mapped to the canonical Platform Principal; caller-supplied tenant/subject fields cannot override that identity.

**Disposition:** Closed by merged revision `f7ed027a1db33b13594502131784105302cabc09`; exact-head and post-merge CI, CodeQL, secret scan, R10 certification and reference-agent checks passed.

### P2-02 — Revocation was not enforced

**Finding:** Token identifiers were required but not checked against a revocation source.

**Remediation:** Platform PR #105 introduced an issuer-plus-token-ID revocation contract, a durable single-host SQLite reference adapter and fail-closed handling for unavailable revocation status. Tests cover revocation and revocation-store failure.

**Disposition:** Closed for the reviewed reference implementation. **Production limitation remains:** SQLite is not a shared high-availability revocation service; production requires an operational shared backend and live issuer/JWKS configuration.

### P2-03 — Tenant alias, claim and clock validation gaps

**Finding:** Contradictory tenant aliases and incomplete access-token profile/claim normalization could allow ambiguous or invalid identity context.

**Remediation:** The strict verifier requires configured issuer/audience, allowlisted algorithms, access-token type, key identifier, client identity, subject, tenant and principal type; checks expiry/issued-at with bounded leeway; and rejects contradictory tenant/scope representations and malformed timestamps.

**Disposition:** Closed by exact-SHA JWT tests and the canonical P2 conformance suite.

### P2-04 — Object-level tenant authorization on event/evidence reads

**Finding:** The cross-repository adversarial regression discovered that foreign-tenant `runs.events` and `runs.evidence` requests returned HTTP 200 with empty arrays. No foreign payload was returned, but the gateway did not explicitly authorize ownership of the run ID before the read. This was an authorization defect, not a harmless empty result.

**Remediation:** Platform PR #106 added an explicit run-existence/tenant-ownership check before both operations and identical denial for foreign and unknown run IDs, avoiding resource-existence enumeration. Unit tests cover same-tenant success, foreign-tenant denial and unknown-run denial. The cross-cutting HTTP adversarial regression now requires 403 for cross-tenant event/evidence reads.

**Disposition:** Closed by merged revision `c094160a243382b043f40bb642f758a30e6203ff`; all exact-head and post-merge Platform gates passed, and the refreshed ecosystem adversarial/conformance workflow passed.

### P2-05 — Cross-repository context and certification evidence

**Finding:** A passing Platform unit suite alone would not prove that OS and SDK preserve identity context without creating a second authority, or that the reviewed baseline actually exercises the real resolver.

**Remediation:** TADL's canonical P2 gate verifies exact locked OS/SDK/Platform revisions, runs Platform JWT/resolver/authorization tests, OS adapter contract tests, SDK tenant-context tests, the cross-cutting HTTP adversarial regression and the TSIC authority gate. It also verifies that P3–P10 remain not started until P2 passes.

**Disposition:** Closed by TADL merge revision `0347f96c3f1498a178c3723111eca98de80fd6eb`; all exact-head and post-merge CI/security/conformance checks passed.

## Exact workflow evidence

- Platform PR #105 exact-head: CI `39072748116`, CodeQL `39072748123`, Secret Scan `39072748182`, R10 `39072748140`, Reference Agents `39072748142` — success.
- Platform PR #105 post-merge: CI `39072823742`, CodeQL `39072823772`, Secret Scan `39072823754`, R10 `39072823777`, Reference Agents `39072823746` — success.
- Platform PR #106 exact-head: CI `39073135750`, CodeQL `39073135715`, Secret Scan `39073135744`, R10 `39073135701`, Reference Agents `39073135709` — success.
- Platform PR #106 post-merge: CI `39073213543`, CodeQL `39073213506`, Secret Scan `39073213560`, R10 `39073213490`, Reference Agents `39073213489` — success.
- TADL P2 PR #66 exact-head: CI `39073444276`, CodeQL `39073444279`, Security `39073444274`, Secret Scan `39073444265`, Ecosystem Integration `39073444287` — success.
- TADL P2 post-merge: CI `39073528740`, CodeQL `39073528521`, Security `39073528541`, Secret Scan `39073528649`, Scorecard `39073528590`, Release Attestations `39073528526`, Ecosystem Integration `39073528687` — success.

The post-merge Ecosystem Integration run executed the TSIC authority gate, contract smoke test, ecosystem conformance, governed-execution adversarial regression, canonical P2 identity/tenancy conformance, team-delegation regression and ecosystem component regression.

## Residual risks — deliberately not certified

- Live production IdP, trusted production issuer/JWKS endpoints and operational key rotation are not verified.
- The SQLite revocation adapter is single-host only; shared HA revocation, backup/restore and operational revocation SLAs are not verified.
- Production TLS/reverse proxy, monitoring/alerting, incident response, tenant provisioning and production data-plane isolation are not verified.
- This phase certifies the reviewed repository/reference behavior only. It does not certify deployment, capacity, independent penetration testing or production readiness.

## Exit decision

P2's repository/reference exit gate is satisfied. The manifest marks P2 `certified`, P3 as the next eligible phase and P4–P10 as `not_started`. Proceed to P3 event delivery/durability only after this closeout's own CI, security, TSIC and post-merge checks are green. Do not describe external production readiness as complete.
