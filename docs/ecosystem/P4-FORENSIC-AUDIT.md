# P4 Forensic Audit — Trace Lineage and Evidence Integrity

**Disposition:** PASS — certified for repository/reference conformance  
**Audit date:** 2026-10-18  
**Active next phase:** P5 — canonical service, agent and contract registries  
**Production telemetry/deployment:** unverified

## Reviewed revision register

| Component | Reviewed revision | Evidence |
|---|---|---|
| TSIC | `dab1fbaa87c97648eb3908daccf4f8a5d90a70ef` | PR #72 merged; canonical trace-context schema, contract descriptor, zero-ID negative tests and TSIC CI passed |
| Platform SDK | `2f358d5dd1e562918613f138b7ef1e3a16f693cb` | PR #51 merged; trace-lineage model, W3C traceparent/correlation propagation, tests, typing, security and package smoke passed |
| Agent OS | `62826433a3110f7d29fd8dc7295efa584fa7934e` | PR #138 merged; persisted span lineage, migration for existing event tables, OS tests, CodeQL and OpenSSF Scorecard passed |
| Agent Platform | `35273b514b960daecb7bdcd8ed03dbf12117a514` | PR #111 merged; tenant-bound request/audit/approval/tool/evidence context, Python 3.12/3.13/3.14 quality, SQL, R10, reference-agent, CodeQL and secret scan passed |
| TADL | `ebc7f63329d65e179c7aaa22f4158eeee7c9bb16` | PR #69 merged after exact-SHA ecosystem integration and P4 trace-lineage reconstruction passed |

## Workflow evidence

- TSIC PR #72 head `09a6d79ddb695c9736a88ed2a4ef5744deecc63a`: TSIC CI and certification workflows passed before merge.
- SDK PR #51 head `cb9989b4cb983957ebd630dc8a08e3f1a2193f0d`: CI `39102057983` PASS; Security `39102058038` PASS.
- OS PR #138 head `c8653d93df33a887ba26376f90c12f8df8887709`: CI `39102355027` PASS; CodeQL `39102355004` PASS; OpenSSF Scorecard `39102354971` PASS.
- Platform PR #111 head `60450083671d5a4df8b7454e5e391d1292ea33d6`: CI `39102447974` PASS; reference agents `39102447981` PASS; CodeQL `39102447989` PASS; R10 `39102448003` PASS; secret scan `39102448057` PASS.
- TADL PR #69 head `71ad0fa07995a11b6079bf4284c891310400bf52`: CI `39102567220` PASS; CodeQL `39102567227` PASS; secret scan `39102567232` PASS; Security `39102567258` PASS; ecosystem integration `39102567226` PASS.

## Exit-gate audit

1. **Canonical contract:** TSIC owns the versioned JSON Schema and contract descriptor. The schema rejects zero-valued trace/span IDs, unknown top-level fields and authority-shaped extensions.
2. **Typed propagation:** SDK, Platform and OS define matching trace-lineage models with non-zero W3C IDs, stable request/correlation/tenant scope, parent span, bounded safe attributes and digest-addressed evidence.
3. **W3C propagation:** SDK, Platform and OS expose `traceparent`, `x-correlation-id` and `x-request-id` headers. The existing SDK W3C `TraceContext` API remains available; the lineage model is separate to avoid a breaking API rename.
4. **Platform record linkage:** request context, policy decision, approval request, tool call, audit record, evidence reference and evidence link can carry trace lineage. Request/audit/approval/tool/evidence tenant bindings fail closed when they disagree.
5. **Event persistence:** OS event rows store span and parent-span IDs, migrate existing tables without destructive rebuild, and emit span ID in the CloudEvents envelope. Generated default span IDs use valid 64-bit W3C width.
6. **Evidence integrity:** evidence references require a lowercase SHA-256 digest and bounded identifiers. The trace schema carries references/digests, not raw payloads.
7. **End-to-end reconstruction:** TADL's exact-SHA P4 gate reconstructs a seven-span chain across SDK, Platform and OS contexts, validates each against the pinned TSIC schema, checks parent linkage, shared trace/tenant/correlation scope, unique spans and evidence digest preservation, and verifies that authority-shaped fields are rejected.
8. **Regression safety:** P2 adversarial and identity/tenancy gates, P3 event delivery gate, ecosystem component regression gate, security workflows and exact-SHA registry/contract validation remain in the required integration sequence.
9. **Authority boundary:** trace metadata is observational. It never creates principal identity, tenant membership, policy permission, approval, budget, secret or execution authority. Platform remains the sole generic consequential execution authority.

## Residual risks and limits

- The P4 gate reconstructs a reference trace from typed records; it does not prove a production OpenTelemetry collector, distributed tracing backend, live log sink, alerting, retention policy or operator dashboard is deployed.
- Trace IDs and safe attributes are validated, but production-grade redaction must also be enforced at every exporter/logging adapter and verified with live telemetry.
- Evidence digest presence does not prove source authenticity or business truth; evidence verification remains a separate control.
- External production deployment and production recovery remain unverified and are reserved for P10 certification.

## Final decision

P4 meets its repository/reference exit gate and is marked certified. P5 may begin as the next serial phase. Production observability deployment is not certified by this audit.
