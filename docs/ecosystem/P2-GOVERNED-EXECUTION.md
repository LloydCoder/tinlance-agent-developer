# P2 — Governed Execution Certification

P2 certifies the end-to-end governed execution path:

`TADL declaration → Agent OS lifecycle/context → SDK transport → Platform identity/tenant/policy/approval/budget/sandbox/tool authority → execution → evidence/events → OS result → Transformation outcome`

## Boundary attacks

The P2 adversarial suite must fail closed for:

- forged or invalid bearer credentials;
- request-body tenant spoofing;
- request-body subject spoofing;
- conflicting reuse of an idempotency key;
- cross-tenant execution attempts;
- authority metadata supplied by an untrusted caller;
- caller-selected risk that attempts to downgrade the immutable registered tool risk;
- critical tool execution that produces output before required approval.

The suite is intentionally contract-level. It does not treat the reference HTTP server as production infrastructure.

## Authority law

`effective authority = authenticated principal ∩ tenant ∩ registered capability ∩ policy ∩ risk constraints ∩ required approval ∩ budget ∩ sandbox ∩ secret scope ∩ execution context`

No Transformation field, model output, memory item, retrieved document, tool result, MCP declaration, catalog entry, peer-agent message, or evaluation score can grant authority.

## Exit gate

P2 is complete only when the adversarial certification script and the existing ecosystem conformance suite are green against a reviewed P2 candidate lock derived from the certified P1 baseline. The P2 lock must pin the merged registered-tool-risk enforcement commit rather than accidentally testing against the older P1 Platform revision. CI, CodeQL, security, secret scan and ecosystem integration must all be green on the exact candidate head before merge. The manifest must mark P2 in progress while this gate is being evaluated, and P3-P10 must remain not started. After merge, refresh the lock to exact merged SHAs and record a post-merge certification run.


## P2 post-merge certification evidence — 2026-10-17

**P2 implementation PR:** [#56](https://github.com/LloydCoder/tinlance-agent-developer/pull/56)  
**Merged implementation revision:** `652f5e7c14ccbab5da76023f3fd242b77eb4a3ab`  
**Reviewed Platform risk-enforcement revision:** `1cd2cd2c32628ce5079979b935ed346bebd4733c`

Post-merge workflow evidence on the exact merged TADL revision:

- CI: [39067316989](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067316989) — success
- Ecosystem Integration: [39067317052](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067317052) — success
- CodeQL: [39067317021](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067317021) — success
- Security: [39067317024](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067317024) — success
- Secret Scan: [39067316987](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067316987) — success
- Scorecard: [39067316982](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067316982) — success
- Release Attestations: [39067316997](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39067316997) — success

The ecosystem gate passed P2 adversarial certification against the candidate lock containing the merged Platform registered-risk enforcement. The tests cover forged/invalid credentials, tenant and subject spoofing, API-version enforcement, W3C trace context, content type, oversized Content-Length rejection, idempotency, cross-tenant cancellation, approval authority, caller risk downgrade, critical-action approval gating, run events and evidence retrieval.

The final lock refresh in this closeout PR pins the reviewed P2 TADL implementation revision and Platform risk-enforcement revision. This certificate covers repository/reference conformance only; live production infrastructure remains unverified.
