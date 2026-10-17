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
