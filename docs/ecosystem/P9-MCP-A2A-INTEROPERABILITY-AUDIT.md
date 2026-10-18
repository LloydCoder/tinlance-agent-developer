# P9 Forensic Audit — MCP/A2A Interoperability and Security

**Canonical scope:** P9 in `docs/ecosystem/PHASE-MATRIX.md`.  
**Reviewed baseline:** `ecosystem-p9-mcp-a2a-2026-10-18`.  
**Status:** implementation work in progress; no P9 certification claim is made by static metadata or TSIC-16 status alone.

## Research baseline

- MCP is pinned to the official `2026-07-28` specification. The official release describes a stateless request model, `MCP-Protocol-Version`, `Mcp-Method` and `Mcp-Name` headers, protocol/authentication hardening, and explicit request metadata. Source: [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/).
- A2A is pinned to `1.0.0`; the TSIC interoperability baseline already records this version and defines A2A as agent-to-agent communication. Source: [A2A 1.0.0 specification](https://a2a-protocol.org/v1.0.0/specification/).
- TSIC remains the integration/certification authority. Agent Platform remains the sole identity, tenant, policy, approval, budget, sandbox and consequential-execution authority.

## Findings from the reviewed implementation

### P9-01 — Platform has an MCP tool gateway, not a complete remote MCP protocol entry point

`packages/mcp/.../gateway.py` enforces a Platform-issued permit, tenant binding, capability/resource matching, approval verification, bounded argument structures and single-use in-process permits. It is useful authority-boundary logic, but it is not a Streamable HTTP MCP server. The Platform HTTP boundary currently exposes only `/v1/agent-platform`; no `/mcp` route performs MCP protocol/version negotiation, `server/discover`, `tools/list`, or `tools/call` handling.

**Required remediation:** add a version-pinned, stateless MCP adapter wired to authenticated Platform dispatch; require consistency between body methods/tool names and protocol headers; enforce allowed-Origin validation when Origin is present; bound request/response size and execution time; preserve trace context and idempotency; ensure every tool call is re-authorized by Platform.

### P9-02 — SDK MCP surface is metadata-only and its validation is too permissive for remote use

`src/tinlance_agent_platform_sdk/mcp.py` correctly declares itself metadata-only and excludes bearer tokens/client secrets from its auth model. However, the transport model allows arbitrary HTTP endpoints and runtime protocol-version values can bypass the `Literal` type hint; arbitrary metadata keys/values are not screened for credential material.

**Required remediation:** validate the supported protocol-version set at runtime, require HTTPS for remote endpoints (allow cleartext only for explicit loopback development), reject URL userinfo/fragments and invalid ports, and reject credential-shaped metadata. The SDK must remain a typed client contract, not an authority source.

### P9-03 — A2A Agent Card trust is syntactic, not cryptographic

`AgentCard.validate()` requires HTTPS by default and rejects obvious credential strings in authentication-scheme names. Its optional `signature` is only checked for non-emptiness; no verifier, key identity, canonical signing payload or trust-store lookup exists. An endpoint may also target a private/loopback/link-local address, and hostname resolution/rebinding is not handled.

**Required remediation:** implement a verifiable Agent Card signature/trust interface, canonical card digest, trusted key ID/algorithm policy, and an outbound endpoint validation boundary. For outbound requests, resolve and validate all addresses, reject loopback/private/link-local/multicast/reserved targets, revalidate redirects, and require the transport to pin the validated destination to prevent DNS-rebinding SSRF.

### P9-04 — Remote delegation is attenuated but not expiring

`RemoteDelegation.issue()` correctly rejects capability widening and records tenant/resource scope and a nonce. It has no `issued_at`, `expires_at`, audience, issuer identity or validation method, despite the TSIC contract requiring scoped and expiring delegation.

**Required remediation:** add bounded expiry and audience/issuer binding, reject expired/future-invalid delegations, make the scope/capability set immutable, and test that a child delegation cannot widen parent capabilities or cross tenants.

### P9-05 — TSIC interoperability certification is largely static

TSIC's interoperability gate pins MCP `2026-07-28` and A2A `1.0.0`, asserts authority boundaries and required security rules, and is valuable contract evidence. It does not by itself prove that the deployed Platform HTTP server implements either protocol or that authenticated requests actually traverse the governed execution boundary.

**Required remediation:** extend the TADL ecosystem integration gate to execute protocol-level tests against the exact locked Platform revision, include negative tenant/approval/replay/Origin/SSRF cases, and reconcile the resulting evidence to the TSIC interoperability baseline. Do not relabel TSIC-16 as canonical P9; the numbering systems are independent.

### P9-06 — Canonical phase documents had a phase-number collision

`P9-REFERENCE-ENTERPRISE.md` describes the reference-workforce capability suite and `P10-REPLICATION-GA.md` describes replication fixtures. The canonical phase matrix defines P9 as MCP/A2A interoperability and P10 as end-to-end recovery/production certification. These legacy capability documents are being explicitly reclassified as cross-cutting supporting evidence, not canonical phase definitions.

## P9 acceptance gate

- [ ] Platform exposes authenticated MCP `2026-07-28` requests through a stateless HTTP entry point; body/header mismatch fails closed.
- [ ] MCP `server/discover`, `tools/list`, and `tools/call` use bounded payloads, Origin allowlisting, identity/tenant binding, trace propagation and idempotency.
- [ ] A2A `1.0.0` Agent Card and message/task entry points are authenticated/scoped; remote delegation cannot widen authority and expires.
- [ ] Agent Cards are verified against a trusted key policy; remote endpoint validation blocks SSRF and redirect/DNS-rebinding paths.
- [ ] SDK protocol metadata validates at runtime but grants no authority; OS composes protocol workflows without duplicating Platform authorization.
- [ ] TSIC and TADL execute exact-SHA positive and adversarial protocol tests against the same lock/manifest/registry baseline.
- [ ] Four implementation repositories and TSIC conformance workflows are green on exact reviewed revisions; P9 post-phase audit passes.
- [ ] Production deployment is reported separately; no claim of a live MCP/A2A service without environment evidence.

## Production boundary

Repository conformance cannot prove TLS termination, OAuth issuer/audience configuration, Origin allowlist deployment, outbound network egress controls, distributed rate limiting, remote-agent key management, telemetry or production task persistence. These require environment-level evidence and failure/load testing.
