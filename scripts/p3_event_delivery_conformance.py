#!/usr/bin/env python3
"""Cross-repository P3 event envelope conformance against the pinned TSIC schema."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TSIC = Path("/tmp/tinlance-tsic")
SCHEMA_PATH = TSIC / "schemas/event-envelope.schema.json"
SEMANTICS_PATH = TSIC / "contracts/events/delivery-semantics.json"


def main() -> None:
    if not SCHEMA_PATH.is_file() or not SEMANTICS_PATH.is_file():
        raise SystemExit("FAIL P3: exact pinned TSIC event schema/semantics not materialized")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    semantics = json.loads(SEMANTICS_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    envelopes: dict[str, dict[str, object]] = {}

    from tinlance_agent_platform_events.envelope import CloudEventEnvelope
    from tinlance_agent_platform_sdk.events import CloudEvent
    from tinlance_agent_os.event_runtime import EventSignalRuntime

    common = {
        "source": "https://tinlance.com/platform/runs",
        "type": "com.tinlance.execution.completed.v1",
        "time": "2026-10-18T04:00:00Z",
        "tenantid": "tenant-p3-conformance",
        "executionid": "run-p3-conformance",
        "traceid": "4bf92f3577b34da6a3ce929d0e0e4736",
        "correlationid": "workflow-p3-conformance",
        "data": {"state": "succeeded", "fixture": True},
    }
    envelopes["sdk"] = CloudEvent(id="event-sdk-p3", **common).as_payload()
    envelopes["platform"] = CloudEventEnvelope(
        id="event-platform-p3", **common
    ).as_payload()
    with tempfile.TemporaryDirectory(prefix="tinlance-p3-events-") as tmp:
        runtime = EventSignalRuntime(Path(tmp) / "events.sqlite3", retry_base_seconds=0)
        os_event = runtime.publish(
            tenant_id="tenant-p3-conformance",
            workspace_id="workspace-p3-conformance",
            event_type="com.tinlance.task.completed.v1",
            payload={"state": "succeeded", "fixture": True},
            correlation_id="workflow-p3-conformance",
            dedupe_key="task-p3-conformance-completed",
            trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
        )
        envelopes["os"] = os_event.as_payload()

    failures: list[str] = []
    for producer, envelope in envelopes.items():
        errors = sorted(validator.iter_errors(envelope), key=lambda item: list(item.path))
        if errors:
            failures.append(
                f"{producer} envelope: " + "; ".join(error.message for error in errors)
            )
        if envelope.get("tenantid") != "tenant-p3-conformance":
            failures.append(f"{producer} envelope lost tenant scope")
        if "authorization" in envelope or "capabilitygrant" in envelope:
            failures.append(f"{producer} envelope contains authority-shaped metadata")

    delivery = semantics.get("delivery", {})
    if delivery.get("delivery_guarantee") != "at-least-once":
        failures.append("delivery semantics must be explicitly at-least-once")
    if delivery.get("deduplication_key") != ["source", "id"]:
        failures.append("deduplication must use CloudEvents source + id")
    if delivery.get("outbox_required_for_durable_publish") is not True:
        failures.append("durable producers must use an outbox")
    if delivery.get("inbox_required_for_idempotent_consume") is not True:
        failures.append("idempotent consumers must use an inbox")

    if failures:
        raise SystemExit("FAIL P3 event conformance:\n- " + "\n- ".join(failures))
    print("PASS P3: SDK, Platform and OS envelopes validate against the exact pinned TSIC schema")


if __name__ == "__main__":
    main()
