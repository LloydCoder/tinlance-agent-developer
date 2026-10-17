# P3 — Trusted Agent Identity & Authority Certification

P3 certifies the identity chain already implemented by Agent Platform:

`human/workload principal → authenticated agent identity → agent version → tenant → capability → policy → risk → approval → execution → evidence`

## Certified Platform controls

- real identity/JWKS verification;
- issuer/audience and token lifecycle validation;
- tenant binding and fail-closed authorization;
- explicit authorization policy;
- cryptographic attestation and revocation;
- identity and authorization regression tests.

The developer plane, OS and SDK may carry identity references, but none can mint authority. Delegation can only attenuate authority; it cannot widen the parent's effective capability set.

## External alignment

P3 is aligned with current NIST agent identity/authorization work and least-privilege principles. External guidance informs the control model; executable Platform tests remain authoritative.

## Exit gate

The ecosystem workflow must certify the locked Platform revision and all repository CI/security gates must remain green.


## P3 forensic execution gate — 2026-10-17

The P3 workflow must do more than check for source-code markers. Against the exact locked Platform revision it now executes:

- `tests/test_identity_jwt.py`: signature/algorithm, issuer, audience, expiry, nonce, tenant claim, and HTTPS JWKS configuration.
- `tests/test_authorization_enforcement.py`: approval-to-intent binding and fail-closed behavior.
- `tests/test_m22_identity_crypto_attestation.py`: token claim/time/nonce validation, active key lifecycle, attestation expiry, and revocation semantics.

The phase gate still distinguishes contract-level tests from production identity-provider/JWKS deployment. A successful run does not prove live issuer configuration, JWKS reachability, KMS/HSM deployment, operational revocation propagation, or production tenant configuration.


## P3 post-merge certification evidence — 2026-10-17

**Implementation PR:** [#58](https://github.com/LloydCoder/tinlance-agent-developer/pull/58)  
**Merged implementation revision:** `11316564e7d08bafea11cdfd401f1af134f39069`  
**Reviewed Platform revision:** `1cd2cd2c32628ce5079979b935ed346bebd4733c`

Post-merge workflow evidence on the exact merged TADL revision:

- CI: [39067911789](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911789) — success
- Ecosystem Integration: [39067911822](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911822) — success
- CodeQL: [39067911785](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911785) — success
- Security: [39067911791](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911791) — success
- Secret Scan: [39067911842](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911842) — success
- Scorecard: [39067912766](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067912766) — success
- Release Attestations: [39067911827](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067911827) — success

The exact locked identity/JWKS, approval-binding, and attestation revocation/expiry regression suites passed. The certification is limited to repository/reference behavior; live identity-provider configuration, JWKS availability, KMS/HSM operations, production revocation propagation, and production tenant configuration remain unverified.
