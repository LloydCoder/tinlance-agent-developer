# P6 — Model and Tool Routing Mediation

**Status:** in progress; not certified until exact-SHA cross-repository conformance and post-merge workflows pass.

## Reviewed implementation

- Agent Platform merge: `57ea98c4060b6ca3fab1280b671a28f3b626ea6b`.
- TSIC routing authority: `LloydCoder/tinlance-system-integration` at `e98613c56c7cc52e063557987bb5436cfb24d207`.
- Platform route selection is deterministic and conjunctive across task policy, model capability, tenant/agent allowlists, risk class and score, data classification, cost budget, route enablement, and provider availability.
- Route registration requires an injected trusted Platform registry verifier. Registry denial or outage fails closed.
- The policy version is sourced from the verified route record rather than caller input.
- Allow and deny decisions are recorded before being returned. Evidence-store failure fails closed.
- Model routing does not grant tool execution authority. Platform authorization, approval, budget, secret, sandbox and tool-permit gates remain authoritative.

## Conformance gates

- Platform exact-head CI, type/lint/format, coverage, SQL, TSIC, R10, CodeQL, Reference Agents and Secret Scan passed before merge.
- The TADL cross-repository gate validates the exact TSIC routing-authority contract, trusted policy provenance, cross-tenant denial, and fail-closed evidence recording.
- P6 is not certified until this TADL PR and its exact-SHA ecosystem integration workflow pass and the merged TADL revision's post-merge workflows are green.

## Residual limitations

Provider health/availability must be supplied by trusted Platform runtime context; the router does not itself probe providers. The decision recorder and registry verifier are injected interfaces; a passing repository test does not prove a live production evidence store, route registry, model provider, provider credentials, telemetry backend or production deployment. Those remain unverified unless independently evidenced.
