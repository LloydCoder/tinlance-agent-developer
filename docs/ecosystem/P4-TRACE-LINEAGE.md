# P4 Trace Lineage and Evidence Contract

**Status:** certified for repository/reference conformance  
**Canonical schema:** `schemas/trace-context/v1/trace-context.schema.json`  
**Authority:** TSIC defines the versioned schema; Platform is the only consequential execution authority.

## Contract

- W3C trace IDs and span IDs are lowercase hexadecimal, fixed-width, non-zero identifiers. Child spans preserve trace ID and reference a parent span.
- `correlation_id`, `request_id`, and `tenant_id` are required. Workspace and execution IDs are propagated when applicable.
- The same trace can link request, policy decision, approval, execution, tool call, event, audit record and evidence reference.
- Evidence references carry immutable SHA-256 digests, source labels and optional observation timestamps; presence of a digest does not itself establish that evidence is trustworthy.
- Safe attributes are allow-listed and bounded. Credentials, tokens, raw prompts, cookies and sensitive payloads are not accepted as trace attributes.
- SDK, Platform and OS lineage models expose W3C `traceparent` and correlation/request headers. OS event records persist span/parent-span lineage and emit the span ID as a CloudEvents extension.
- Trace metadata is observational and never grants identity, tenant, policy, approval, budget, secret or execution authority.

## Cross-repository conformance

The TADL P4 gate materializes exact reviewed TSIC, SDK, Platform and OS revisions; constructs a seven-span chain (request → policy → approval → execution → tool → event → evidence); validates every payload against the pinned TSIC schema; checks tenant/trace continuity, parent links, unique span IDs and evidence digests; and verifies that authority-shaped fields are rejected.

## Limits

The P4 gate verifies typed contracts, event persistence behavior, schema conformance and reference-level reconstruction. It does not prove that a production OpenTelemetry collector, distributed tracing backend, live log sink, alerting system or production retention policy is deployed. Those remain deployment/operational evidence requirements for P10.
