#!/usr/bin/env python3
"""P4 cross-repository trace lineage and evidence integrity conformance."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TSIC = Path("/tmp/tinlance-tsic")
SCHEMA_PATH = TSIC / "schemas/trace-context/v1/trace-context.schema.json"
CONTRACT_PATH = TSIC / "contracts/tracing/trace-context.json"


def main() -> None:
    if not SCHEMA_PATH.is_file() or not CONTRACT_PATH.is_file():
        raise SystemExit("FAIL P4: pinned TSIC trace-context schema/contract not materialized")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if contract.get("format") != "tinlance-trace-context/v1":
        raise SystemExit("FAIL P4: TSIC trace context format declaration drifted")

    from tinlance_agent_platform_contracts.trace_context import (
        TraceEvidenceRef as PlatformEvidenceRef,
        TraceLineageContext as PlatformTraceContext,
    )
    from tinlance_agent_os.trace_context import (
        TraceEvidenceRef as OSEvidenceRef,
        TraceLineageContext as OSTraceContext,
    )
    from tinlance_agent_platform_sdk.trace_context import (
        TraceEvidenceRef as SDKEvidenceRef,
        TraceLineageContext as SDKTraceContext,
    )

    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    started = "2026-10-18T05:00:00Z"
    request = SDKTraceContext(
        trace_id=trace_id, span_id="00f067aa0ba902b7", correlation_id="corr-p4-1",
        request_id="req-p4-1", tenant_id="tenant-p4-a", workspace_id="workspace-p4-a",
        operation="agent.request", started_at=started,
        safe_attributes=(("service", "sdk"), ("outcome", "started")),
    )
    policy = PlatformTraceContext(
        trace_id=trace_id, span_id="1111111111111111", parent_span_id=request.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        operation="platform.policy.evaluate", started_at=started,
        decision_id="decision-p4-1", policy_decision_id="policy-p4-1",
        safe_attributes=(("service", "platform"), ("outcome", "succeeded")),
    )
    approval = PlatformTraceContext(
        trace_id=trace_id, span_id="2222222222222222", parent_span_id=policy.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        operation="platform.approval.resolve", started_at=started,
        decision_id=policy.decision_id, approval_id="approval-p4-1",
        safe_attributes=(("service", "platform"), ("outcome", "succeeded")),
    )
    execution = PlatformTraceContext(
        trace_id=trace_id, span_id="3333333333333333", parent_span_id=approval.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        execution_id="execution-p4-1", operation="platform.execution.run", started_at=started,
        approval_id=approval.approval_id,
        safe_attributes=(("service", "platform"), ("outcome", "succeeded")),
    )
    tool = PlatformTraceContext(
        trace_id=trace_id, span_id="4444444444444444", parent_span_id=execution.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        execution_id=execution.execution_id, tool_call_id="tool-call-p4-1",
        operation="platform.tool.invoke", started_at=started,
        safe_attributes=(("service", "platform"), ("outcome", "succeeded"), ("attempt", 1)),
    )
    evidence_digest = "a" * 64
    event = OSTraceContext(
        trace_id=trace_id, span_id="5555555555555555", parent_span_id=tool.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        execution_id=execution.execution_id, event_id="event-p4-1",
        tool_call_id=tool.tool_call_id, operation="os.event.publish", started_at=started,
        evidence_refs=(OSEvidenceRef(
            evidence_id="evidence:p4:1", kind="tool-result", sha256=evidence_digest,
            source="platform.tool.invoke", observed_at=started,
        ),),
        safe_attributes=(("service", "os"), ("outcome", "succeeded")),
    )
    evidence = PlatformTraceContext(
        trace_id=trace_id, span_id="6666666666666666", parent_span_id=event.span_id,
        correlation_id=request.correlation_id, request_id=request.request_id,
        tenant_id=request.tenant_id, workspace_id=request.workspace_id,
        execution_id=execution.execution_id, event_id=event.event_id,
        operation="platform.evidence.record", started_at=started,
        evidence_refs=(PlatformEvidenceRef(
            evidence_id="evidence:p4:1", kind="tool-result", sha256=evidence_digest,
            source="platform.tool.invoke", observed_at=started,
        ),),
        safe_attributes=(("service", "platform"), ("outcome", "succeeded")),
    )

    payloads = [
        ("request", request.as_payload()),
        ("policy", policy.as_payload()),
        ("approval", approval.as_payload()),
        ("execution", execution.as_payload()),
        ("tool", tool.as_payload()),
        ("event", event.as_payload()),
        ("evidence", evidence.as_payload()),
    ]
    failures: list[str] = []
    for name, payload in payloads:
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
        if errors:
            failures.append(f"{name} context: " + "; ".join(error.message for error in errors))
        if payload.get("trace_id") != trace_id or payload.get("tenant_id") != request.tenant_id:
            failures.append(f"{name} lost trace or tenant context")
        if any(key.lower() in {
            "authorization", "cookie", "password", "secret", "token", "api_key",
            "private_key", "credential", "prompt", "raw_payload",
        } for key in payload):
            failures.append(f"{name} context contains a sensitive top-level field")

    spans = {payload["span_id"] for _, payload in payloads}
    for name, payload in payloads:
        parent = payload.get("parent_span_id")
        if parent is not None and parent not in spans:
            failures.append(f"{name} context has an orphan parent span")
    if len(spans) != len(payloads):
        failures.append("trace contains duplicate span identifiers")
    if evidence.as_payload()["evidence_refs"][0]["sha256"] != evidence_digest:
        failures.append("evidence digest lineage was not preserved")
    if [payload["span_id"] for _, payload in payloads] != [
        request.span_id, policy.span_id, approval.span_id, execution.span_id,
        tool.span_id, event.span_id, evidence.span_id,
    ]:
        failures.append("trace chain ordering is inconsistent")

    # A schema-valid trace remains observational; an attempted authority field fails closed.
    forged = dict(request.as_payload())
    forged["authorization"] = "allow"
    if validator.is_valid(forged):
        failures.append("trace schema accepts authority-shaped fields")

    if failures:
        raise SystemExit("FAIL P4 trace lineage:\n- " + "\n- ".join(failures))
    print(json.dumps({
        "phase": "P4",
        "scope": "SDK request -> Platform policy/approval/execution/tool -> OS event -> evidence",
        "spans": len(payloads),
        "trace_id": trace_id,
        "tenant_id": request.tenant_id,
        "evidence_sha256": evidence_digest,
        "status": "pass",
        "production_status": "unverified",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
