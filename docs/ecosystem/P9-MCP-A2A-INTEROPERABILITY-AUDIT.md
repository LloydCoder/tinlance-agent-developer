# P9 Forensic Audit — MCP/A2A Interoperability and Security

**Canonical scope:** P9 in `docs/ecosystem/PHASE-MATRIX.md`.  
**Reviewed baseline:** `ecosystem-p9-mcp-a2a-2026-10-18`.  
**Status:** implementation and adversarial verification in progress. The current P9 PRs add protocol, endpoint and metadata controls, but no P9 certification claim is made until exact-head checks, four-repository integration and post-phase forensic audit pass.

## Research baseline

- MCP is pinned to the official `2026-07-28` specification. The official release describes a stateless request model, `MCP-Protocol-Version`, `Mcp-Method` and `Mcp-Name` headers, protocol/authentication hardening, and explicit request metadata. Source: [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/).
- A2A specification `1.0.1` is the current pinned release; the A2A wire `protocolVersion` remains `1.0`. TSIC's checked-in interoperability baseline still says `1.0.0` and must be reconciled before certification. Source: [A2A 1.0.1 specification](https://a2a-protocol.org/v1.0.1/specification/).
- TSIC remains the integration/certification authority. Agent Platform remains the sole identity, tenant, policy, approval, budget, sandbox and consequential-execution authority.

## Research update — A2A patch release

The official A2A changelog lists specification 1.0.1 dated 2026-05-26, including a fix preferring `application/a2a+json` for HTTP binding. The P9 implementation is pinned to 1.0.1, keeps the wire protocol version at `1.0`, and requires the outbound transport contract to use the updated media type. The TSIC interoperability baseline must be updated to the same specification pin before final certification.

Sources: [A2A official changelog](https://github.com/a2aproject/A2A/blob/main/CHANGELOG.md), [A2A official release](https://github.com/a2aproject/A2A/releases).

## Findings from the reviewed implementation

### P9-01 — Platform has an MCP tool gateway, not a complete remote MCP protocol entry point

`packages/mcp/.../gateway.py` enforces a Platform-issued permit, tenant binding, capability/resource matching, approval verification, bounded argument structures and single-use in-process permits. It is useful authority-boundary logic, but it is not a Streamable HTTP MCP server. The Platform HTTP boundary currently exposes only `/v1/agent-platform`; no `/mcp` route performs MCP protocol/version negotiation, `server/discover`, `tools/list`, or `tools/call` handling.

**Remediation in Platform PR #132:** adds a stateless MCP 2026-07-28 adapter, a mounted `POST /mcp` HTTP route, per-request client identity metadata checks, body/header agreement, Origin validation, request/response bounds, strict argument-schema validation, trace-context validation, idempotency enforcement and dispatch through the injected Platform API boundary. Regression tests exercise the mounted HTTP route and adversarial protocol cases. This remains unmerged and uncertified until the exact head passes all required workflows.

### P9-02 — SDK MCP surface is metadata-only and its validation is too permissive for remote use

`src/tinlance_agent_platform_sdk/mcp.py` correctly declares itself metadata-only and excludes bearer tokens/client secrets from its auth model. However, the transport model allows arbitrary HTTP endpoints and runtime protocol-version values can bypass the `Literal` type hint; arbitrary metadata keys/values are not screened for credential material.

**Remediation in SDK PR #55:** validates protocol versions at runtime, restricts cleartext HTTP to loopback development, rejects embedded credentials/query/fragment data and non-public literal IPs, and blocks credential-shaped or duplicate metadata keys. Regression tests cover endpoint and metadata failures. The SDK remains descriptive metadata only and grants no authority; this PR must pass exact-head quality/security checks before merge.

### P9-03 — A2A Agent Card trust is syntactic, not cryptographic

`AgentCard.validate()` requires HTTPS by default and rejects obvious credential strings in authentication-scheme names. Its optional `signature` is only checked for non-emptiness; no verifier, key identity, canonical signing payload or trust-store lookup exists. An endpoint may also target a private/loopback/link-local address, and hostname resolution/rebinding is not handled.

**Remediation in Platform PR #132:** introduces an injected signature-verifier interface, canonical signing payload, key ID/algorithm allowlist and an outbound endpoint validator that rejects non-public addresses. The transport contract requires pinned validated addresses and forbids redirects. Remaining certification must verify the exact adapter behavior, trusted-key policy supplied by deployment, and adversarial DNS/redirect cases; repository tests do not prove the production transport actually pins sockets.

### P9-04 — Remote delegation is attenuated but not expiring

`RemoteDelegation.issue()` correctly rejects capability widening and records tenant/resource scope and a nonce. It has no `issued_at`, `expires_at`, audience, issuer identity or validation method, despite the TSIC contract requiring scoped and expiring delegation.

**Remediation in Platform PR #132:** delegation records carry issue/expiry timestamps and an explicit audience bound to the remote-agent identity. Validation requires the expected authenticated tenant, trusted issuer and receiver audience, and rejects expired/future-invalid timestamps, invalid TTLs, tenant substitution, issuer substitution and audience substitution. Capability scope remains an immutable frozenset and issuance rejects widening. The negative tests are in the branch; exact-SHA certification remains outstanding.

### P9-05 — TSIC interoperability certification is largely static

TSIC's interoperability gate pins MCP `2026-07-28` and A2A `1.0.1`, asserts authority boundaries and required security rules, and is valuable contract evidence. It does not by itself prove that the deployed Platform HTTP server implements either protocol or that authenticated requests actually traverse the governed execution boundary.

**Required remediation:** the current TADL integration run validates the existing reviewed lock, not yet the unmerged Platform/OS/SDK PR heads. After the implementation PRs merge, refresh the lock and registry to the exact merged SHAs, run the ecosystem integration gate against that baseline, add negative tenant/approval/replay/Origin/SSRF cases, and reconcile evidence to TSIC. Do not relabel TSIC-16 as canonical P9; the numbering systems are independent.

### P9-06 — Canonical phase documents had a phase-number collision

`P9-REFERENCE-ENTERPRISE.md` describes the reference-workforce capability suite and `P10-REPLICATION-GA.md` describes replication fixtures. The canonical phase matrix defines P9 as MCP/A2A interoperability and P10 as end-to-end recovery/production certification. These legacy capability documents are being explicitly reclassified as cross-cutting supporting evidence, not canonical phase definitions.

## P9 acceptance gate

- [ ] Platform exposes authenticated MCP `2026-07-28` requests through a stateless HTTP entry point; body/header mismatch fails closed.
- [ ] MCP `server/discover`, `tools/list`, and `tools/call` use bounded payloads, Origin allowlisting, identity/tenant binding, trace propagation and idempotency.
- [ ] A2A `1.0.1` Agent Card and message/task entry points are authenticated/scoped; remote delegation cannot widen authority and expires.
- [ ] Agent Cards are verified against a trusted key policy; remote endpoint validation blocks SSRF and redirect/DNS-rebinding paths.
- [ ] SDK protocol metadata validates at runtime but grants no authority; OS composes protocol workflows without duplicating Platform authorization.
- [ ] TSIC and TADL execute exact-SHA positive and adversarial protocol tests against the same lock/manifest/registry baseline.
- [ ] Four implementation repositories and TSIC conformance workflows are green on exact reviewed revisions; P9 post-phase audit passes.
- [ ] Production deployment is reported separately; no claim of a live MCP/A2A service without environment evidence.

## Production boundary

Repository conformance cannot prove TLS termination, OAuth issuer/audience configuration, Origin allowlist deployment, outbound network egress controls, distributed rate limiting, remote-agent key management, telemetry or production task persistence. These require environment-level evidence and failure/load testing.
