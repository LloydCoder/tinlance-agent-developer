# P6 — Model and Tool Routing Mediation

**Status:** certified for the reviewed exact-SHA repository/reference scope. This does not certify a live production routing service, provider account, credentials, or external deployment.

## Reviewed implementation

- Agent Platform merge: `a06c32b26a6abde2294154dba9a8d299789b1c37`.
- TADL routing-conformance merge: `2cd0cd75c419535ada51286a1aca4123aa889705`.
- TSIC routing authority pinned for this baseline: `LloydCoder/tinlance-system-integration@e98613c56c7cc52e063557987bb5436cfb24d207`.
- Platform route selection is deterministic and conjunctive across task policy, model capability, tenant/agent allowlists, risk class, data classification, cost budget, route enablement, and provider availability.
- Route registration requires an injected trusted Platform registry verifier. Registry denial or outage fails closed.
- The policy version is sourced from the verified route record rather than caller input.
- Routing context is accepted only after a trusted Platform context verifier passes; denial is recorded, and verifier outage is recorded before failing closed.
- Every routing request requires a valid non-zero W3C trace identifier. Estimated call cost must fit both the route cost ceiling and available budget.
- Allow and deny decisions are recorded before being returned. Evidence-store failure fails closed.
- Model routing does not grant tool execution authority. Platform authorization, approval, budget, secret, sandbox and tool-permit gates remain authoritative.

## Exact-SHA workflow evidence

**Platform merge `a06c32b26a6abde2294154dba9a8d299789b1c37`:**
- [CI](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741552) — success.
- [R10 Certification](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741548) — success.
- [CodeQL](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741560) — success.
- [Reference Agents](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741567) — success.
- [Supply Chain Attestation](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741565) — success.
- [Secret Scan](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39108741602) — success.

**TADL routing-conformance merge `2cd0cd75c419535ada51286a1aca4123aa889705`:**
- [CI](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913539) — success.
- [Ecosystem Integration](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913534) — success.
- [CodeQL](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913522) — success.
- [Security](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913500) — success.
- [Secret Scan](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913524) — success.
- [Supply Chain Attestation](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913528) — success.
- [Release Attestations](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913548) — success.
- [Scorecard](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39108913515) — success.

The cross-repository gate exercised the TSIC routing contract, trusted policy provenance, registered route enforcement, budget/risk alignment, negative controls, cross-tenant denial and fail-closed evidence behavior. The exact merged TADL SHA is now pinned in both the lock and manifest for the post-merge audit baseline.

## Residual limitations

Provider health/availability must be supplied by trusted Platform runtime context; the router does not itself probe providers. The decision recorder and registry verifier are injected interfaces; passing repository tests does not prove a live production evidence store, route registry, model provider, provider credentials, telemetry backend or production deployment. Those remain unverified unless independently evidenced. P7 must separately establish real adapter contracts and integration boundaries; P6 does not claim that work is complete.
