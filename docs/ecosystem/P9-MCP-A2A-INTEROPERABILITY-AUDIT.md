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

**Remediation in Platform PR #132:** introduces an injected signature-verifier interface, canonical signing payload, key ID/algorithm allowlist and an outbound endpoint validator that rejects non-public addresses and query-bearing endpoints. The transport contract requires pinned validated addresses, forbids redirects, and specifies `application/a2a+json` for the 1.0.1 HTTP binding. Outbound calls now require a Platform-backed credential provider to mint a short-lived credential for a validated, tenant/issuer/audience-bound delegation; callers can no longer pass an arbitrary bearer token directly. Remaining certification must verify the trusted-key policy and credential provider supplied by deployment, and adversarial DNS/redirect cases; repository tests do not prove the production transport actually pins sockets.

### P9-04 — Remote delegation is attenuated but not expiring

`RemoteDelegation.issue()` correctly rejects capability widening and records tenant/resource scope and a nonce. It has no `issued_at`, `expires_at`, audience, issuer identity or validation method, despite the TSIC contract requiring scoped and expiring delegation.

**Remediation in Platform PR #132:** delegation records carry issue/expiry timestamps and an explicit audience bound to the remote-agent identity. Validation requires the expected authenticated tenant, trusted issuer and receiver audience, and rejects expired/future-invalid timestamps, invalid TTLs, tenant substitution, issuer substitution and audience substitution. The outbound client checks requested capabilities and exact resource scope against the delegation before obtaining a credential from the injected Platform-backed provider. Capability scope remains an immutable frozenset and issuance rejects widening. The negative tests are in the branch; exact-SHA certification remains outstanding.

### P9-07 — No authenticated A2A server entry point existed

The prior Platform implementation could validate a remote Agent Card and make outbound calls, but the HTTP server did not expose a signed local Agent Card or accept inbound A2A task requests. That left the ecosystem without a complete inbound/outbound protocol boundary.

**Remediation in Platform PR #132:** adds public `GET /.well-known/agent-card.json` for the signed card and authenticated `POST /a2a` for the bounded A2A 1.0 JSON-RPC profile `message/send` and `tasks/get`. Requests resolve the bearer credential to a Platform principal, derive tenant/subject only from that principal, apply a tenant-aware rate limiter, propagate trace context and idempotency, and dispatch `runs.create`/`runs.events` through Platform. The currently implemented profile is intentionally text-only and does not claim streaming, task cancellation, push notifications, or complete coverage of every optional A2A method. Those capabilities must remain absent from the published card until implemented and tested.

### P9-05 — TSIC interoperability certification is largely static

TSIC's current main baseline pins MCP `2026-07-28` and A2A `1.0.0`; TSIC PR #76 updates the canonical policy, gate and certification assertion to A2A `1.0.1`; TSIC PR #77 adds exact assertions for signed-card verification, scoped remote credentials, tenant-scoped idempotency, MCP body/header mismatch behavior, and the A2A HTTP media type. The gate asserts authority boundaries and required security rules, and is valuable contract evidence. It does not by itself prove that the deployed Platform HTTP server implements either protocol or that authenticated requests actually traverse the governed execution boundary.

**Required remediation:** the current TADL integration run validates the existing reviewed lock, not yet the unmerged Platform/OS/SDK PR heads. After the implementation PRs merge, refresh the lock and registry to the exact merged SHAs, run the ecosystem integration gate against that baseline, add negative tenant/approval/replay/Origin/SSRF cases, and reconcile evidence to TSIC. Do not relabel TSIC-16 as canonical P9; the numbering systems are independent.

### P9-06 — Canonical phase documents had a phase-number collision

`P9-REFERENCE-ENTERPRISE.md` describes the reference-workforce capability suite and `P10-REPLICATION-GA.md` describes replication fixtures. The canonical phase matrix defines P9 as MCP/A2A interoperability and P10 as end-to-end recovery/production certification. These legacy capability documents are being explicitly reclassified as cross-cutting supporting evidence, not canonical phase definitions.

### P9-08 — Idempotency keys were globally namespaced

The API reference dispatcher keyed its bounded idempotency cache directly by the caller-provided key. Because the fingerprint includes tenant and subject but the cache key did not, two tenants using the same key could conflict with each other and create a cross-tenant denial-of-service vector.

**Remediation in Platform PR #132:** the dispatcher now namespaces each idempotency key by the authenticated tenant and principal. Regression tests prove that identical caller keys remain isolated across tenants, while same-scope replay returns the prior result and same-scope payload changes fail with an idempotency conflict.

### P9-09 — MCP discovery and error envelopes diverged from the 2026-07-28 schema

The first adapter draft returned a legacy-style `protocolVersion`/body-level `serverInfo` from `server/discover`, omitted `supportedVersions`, cache metadata and result metadata, and used legacy JSON-RPC codes for header mismatch/version rejection. It also incorrectly required `clientInfo`, which is optional in the current schema.

**Remediation in Platform PR #132:** discovery now returns `supportedVersions`, capabilities, `resultType`, `ttlMs`, `cacheScope`, and `io.modelcontextprotocol/serverInfo` under result `_meta`. Successful results are decorated with required `resultType` and server identity metadata. Missing/malformed/mismatched headers use `HeaderMismatch` (-32020) with HTTP 400; an unsupported protocol version uses `UnsupportedProtocolVersion` (-32022) with the supported/requested version data. `clientCapabilities` and protocol version remain required, while `clientInfo` is validated only when supplied. Regression tests assert these exact wire fields and error codes.

Source: [MCP 2026-07-28 discovery schema](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx), [official 2026-07-28 changelog](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/changelog.mdx).

## P9 acceptance gate

- [ ] Platform exposes authenticated MCP `2026-07-28` requests through a stateless HTTP entry point; body/header mismatch fails closed.
- [ ] MCP `server/discover`, `tools/list`, and `tools/call` match the 2026-07-28 schemas, including discovery version list, result metadata/cache fields, exact error codes, bounded payloads, Origin allowlisting, identity/tenant binding, trace propagation, header/body version matching, and tenant-scoped idempotency.
- [ ] A2A `1.0.1` signed Agent Card is published and the authenticated `message/send` and `tasks/get` entry points are scoped; remote delegation cannot widen authority and expires.
- [ ] Inbound Agent Cards are signed; outbound Agent Cards are verified against a trusted key policy; remote endpoint validation blocks SSRF and redirect/DNS-rebinding paths.
- [ ] SDK protocol metadata validates at runtime but grants no authority; OS composes protocol workflows without duplicating Platform authorization.
- [ ] TSIC and TADL execute exact-SHA positive and adversarial protocol tests against the same lock/manifest/registry baseline.
- [ ] Idempotency keys are scoped to authenticated tenant/principal; cross-tenant key collisions and same-scope payload conflicts are tested.
- [ ] Four implementation repositories and TSIC conformance workflows are green on exact reviewed revisions; P9 post-phase audit passes.
- [ ] Production deployment is reported separately; no claim of a live MCP/A2A service without environment evidence.

## Production boundary

Repository conformance cannot prove TLS termination, OAuth issuer/audience configuration, Origin allowlist deployment, outbound network egress controls, distributed rate limiting, remote-agent key management, telemetry or production task persistence. These require environment-level evidence and failure/load testing.
