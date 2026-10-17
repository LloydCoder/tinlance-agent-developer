"""P2 adversarial certification against the real Platform reference gateway.

This test exercises the Platform HTTP boundary, identity binding, tenant
isolation, idempotency, registered-tool risk enforcement, approval gating and
evidence events. It uses deterministic reference stores; it is not production
infrastructure certification.
"""
from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from uuid import UUID, uuid4

PLATFORM_SOURCE = Path("/tmp/tinlance-platform")
if not PLATFORM_SOURCE.is_dir():
    raise SystemExit(
        "P2 requires the Platform source checked out from ecosystem.lock.json at "
        "/tmp/tinlance-platform"
    )
sys.path.insert(0, str(PLATFORM_SOURCE))

from tinlance_agent_platform_agents import AgentRegistry
from tinlance_agent_platform_contracts import AgentDefinition, Principal
from tinlance_agent_platform_events import InMemoryEventStore
from tinlance_agent_platform_evidence import InMemoryEvidenceStore
from tinlance_agent_platform_execution import ExecutionErrorCode
from tinlance_agent_platform_api import AgentPlatformAPI
from tinlance_agent_platform_api.http import MAX_REQUEST_BYTES, serve
from tests.support.reference_gateway import ReferencePlatformGateway, StaticPrincipalResolver

TENANT = "tenant-p2"
SUBJECT = "subject-p2"
TOKEN = "token-p2"
AUTHORIZED_TOKEN = "token-p2-authorized"
APPROVER_SUBJECT = "approver-p2"
APPROVER_TOKEN = "token-p2-approver"
OTHER_TENANT = "tenant-p2-other"
OTHER_SUBJECT = "subject-p2-other"
OTHER_TOKEN = "token-p2-other"
AGENT_ID = UUID("00000000-0000-0000-0000-000000000201")
TASK_ID = UUID("00000000-0000-0000-0000-000000000202")


def post(
    endpoint: str,
    *,
    operation: str,
    tenant: str = TENANT,
    subject: str = SUBJECT,
    token: str = TOKEN,
    payload: dict[str, object] | None = None,
    request_id: str | None = None,
    idempotency_key: str | None = None,
    api_version: str = "1.1",
    traceparent: str | None = None,
    content_type: str = "application/json",
    raw_body: bytes | None = None,
) -> tuple[int, dict[str, object]]:
    envelope = {
        "tenant_id": tenant,
        "subject_id": subject,
        "operation": operation,
        "payload": payload or {},
    }
    body = raw_body if raw_body is not None else json.dumps(
        envelope, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Content-Type": content_type,
        "Authorization": f"Bearer {token}",
        "X-Tinlance-API-Version": api_version,
        "X-Request-ID": request_id or f"p2-{uuid4()}",
    }
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    if traceparent is not None:
        headers["traceparent"] = traceparent
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/agent-platform",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))



def oversized_content_length(endpoint: str) -> tuple[int, dict[str, object]]:
    """Assert header-level size rejection without streaming a megabyte to the server."""
    host = endpoint.removeprefix("http://").split(":", 1)[0]
    port = int(endpoint.rsplit(":", 1)[1])
    request = (
        "POST /v1/agent-platform HTTP/1.1\\r\\n"
        f"Host: {host}:{port}\\r\\n"
        "Content-Type: application/json\\r\\n"
        "X-Tinlance-API-Version: 1.1\\r\\n"
        "X-Request-ID: p2-oversized-content-length\\r\\n"
        f"Content-Length: {MAX_REQUEST_BYTES + 1}\\r\\n"
        "Connection: close\\r\\n\\r\\n"
    ).encode("ascii")
    with socket.create_connection((host, port), timeout=5) as connection:
        connection.sendall(request)
        chunks: list[bytes] = []
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    response = b"".join(chunks)
    head, _, body = response.partition(b"\\r\\n\\r\\n")
    status_line = head.split(b"\\r\\n", 1)[0].decode("ascii", errors="replace")
    try:
        status = int(status_line.split()[1])
        parsed = json.loads(body.decode("utf-8"))
    except (IndexError, ValueError, json.JSONDecodeError) as exc:
        raise AssertionError(f"invalid oversized-request response: {response[:500]!r}") from exc
    if not isinstance(parsed, dict):
        raise AssertionError("oversized-request response body must be an object")
    return status, parsed


def assert_status(
    actual: int, expected: int, description: str, body: dict[str, object]
) -> None:
    if actual != expected:
        raise AssertionError(f"{description}: expected HTTP {expected}, got {actual}: {body}")


def main() -> None:
    events = InMemoryEventStore()
    evidence = InMemoryEvidenceStore()
    agents = AgentRegistry()
    agent = AgentDefinition(
        AGENT_ID,
        TENANT,
        "p2-adversarial-agent",
        "1.0.0",
        SUBJECT,
        "default",
        frozenset({"repository.read", "security.scan", "deployment.trigger"}),
        "a" * 64,
    )
    agents.register(agent)
    gateway = ReferencePlatformGateway(
        agents=agents,
        events=events,
        evidence=evidence,
        approver_subjects=frozenset({APPROVER_SUBJECT}),
    )
    resolver = StaticPrincipalResolver(
        {
            TOKEN: Principal(
                SUBJECT,
                "human",
                TENANT,
                scopes=frozenset({"repository.read", "security.scan"}),
            ),
            AUTHORIZED_TOKEN: Principal(
                SUBJECT,
                "human",
                TENANT,
                scopes=frozenset({"repository.read", "security.scan", "deployment.trigger"}),
            ),
            APPROVER_TOKEN: Principal(
                APPROVER_SUBJECT,
                "human",
                TENANT,
                scopes=frozenset({"approval:decide"}),
            ),
            OTHER_TOKEN: Principal(
                OTHER_SUBJECT,
                "human",
                OTHER_TENANT,
                scopes=frozenset({"repository.read"}),
            ),
        }
    )
    server = serve(AgentPlatformAPI(gateway), resolver, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}"
    try:
        # Authentication and request-envelope boundary.
        status, body = post(endpoint, operation="health", token="forged-token")
        assert_status(status, 401, "invalid bearer token", body)

        status, body = post(
            endpoint, operation="health", tenant=OTHER_TENANT, token=TOKEN
        )
        assert_status(status, 403, "forged tenant", body)

        status, body = post(
            endpoint, operation="health", subject="forged-subject", token=TOKEN
        )
        assert_status(status, 403, "forged subject", body)

        status, body = post(endpoint, operation="health", api_version="999")
        assert_status(status, 426, "unsupported API version", body)

        status, body = post(
            endpoint,
            operation="health",
            traceparent=f"00-{'0' * 32}-{'1' * 16}-01",
        )
        assert_status(status, 400, "zero trace identifier", body)

        status, body = post(
            endpoint,
            operation="health",
            content_type="text/plain",
        )
        assert_status(status, 415, "non-JSON request", body)

        status, body = oversized_content_length(endpoint)
        assert_status(status, 413, "oversized Content-Length", body)

        # Real registered agent, run lifecycle, and HTTP idempotency semantics.
        create_payload = {
            "task_id": str(TASK_ID),
            "agent_id": str(AGENT_ID),
            "intent": "verify governed execution boundary",
        }
        create_key = "p2-run-create-idempotency-0001"
        status, first = post(
            endpoint,
            operation="runs.create",
            payload=create_payload,
            request_id="p2-create-1",
            idempotency_key=create_key,
        )
        assert_status(status, 200, "first run creation", first)
        assert first.get("status") == "accepted"
        first_payload = first.get("payload", {})
        run_id = str(first_payload.get("run_id", ""))
        assert run_id, f"run creation did not return a run ID: {first}"

        status, duplicate = post(
            endpoint,
            operation="runs.create",
            payload=create_payload,
            request_id="p2-create-2",
            idempotency_key=create_key,
        )
        assert_status(status, 200, "idempotent duplicate run creation", duplicate)
        assert duplicate.get("payload", {}).get("run_id") == run_id
        created_events = [
            event for event in events.list_for_run(TENANT, UUID(run_id))
            if event.event_type == "run.created"
        ]
        assert len(created_events) == 1, "idempotent duplicate caused a second run side effect"

        conflict_payload = {**create_payload, "intent": "different intent"}
        status, conflict = post(
            endpoint,
            operation="runs.create",
            payload=conflict_payload,
            request_id="p2-create-3",
            idempotency_key=create_key,
        )
        assert_status(status, 409, "idempotency-key payload conflict", conflict)
        assert conflict.get("error") == "IDEMPOTENCY_CONFLICT"

        status, body = post(
            endpoint,
            operation="runs.cancel",
            tenant=OTHER_TENANT,
            subject=OTHER_SUBJECT,
            token=OTHER_TOKEN,
            payload={"run_id": run_id},
        )
        assert_status(status, 403, "cross-tenant run cancellation", body)

        status, body = post(
            endpoint,
            operation="approvals.decide",
            payload={"approval_id": str(uuid4()), "approved": True},
            token=TOKEN,
        )
        assert_status(status, 403, "non-approver cannot decide approvals", body)

        # A declared capability is not authority. A caller cannot downgrade the
        # registered critical tool to low risk, and a correctly classified
        # critical request still waits for approval before any tool side effect.
        critical_run_payload = {
            "task_id": str(uuid4()),
            "agent_id": str(AGENT_ID),
            "intent": "verify critical-action approval gate",
        }
        status, critical_run = post(
            endpoint,
            operation="runs.create",
            payload=critical_run_payload,
            token=AUTHORIZED_TOKEN,
            idempotency_key="p2-critical-run-create-0001",
        )
        assert_status(status, 200, "critical-action run creation", critical_run)
        critical_run_id = str(critical_run.get("payload", {}).get("run_id", ""))
        assert critical_run_id, f"critical run was not created: {critical_run}"

        tool_payload = {
            "agent_id": str(AGENT_ID),
            "run_id": critical_run_id,
            "capability_id": "deployment.trigger",
            "capability_version": "1",
            "tool_name": "deployment.trigger",
            "tool_version": "1",
            "action": "deploy",
            "resource": "environment:production",
            "risk": "low",
            "reversibility": "reversible",
            "data_class": "internal",
            "blast_radius": "single",
            "requested_timeout_seconds": 30.0,
            "requested_tool_calls": 1,
            "evidence_required": True,
            "contract_version": "governed-execution.v1",
        }
        status, downgraded = post(
            endpoint,
            operation="tools.execute",
            payload=tool_payload,
            token=AUTHORIZED_TOKEN,
            idempotency_key=f"test-risk-downgrade-{uuid4()}",
        )
        assert_status(status, 409, "critical tool risk downgrade", downgraded)
        assert downgraded.get("error") == ExecutionErrorCode.AUTHORIZATION_DENIED.value

        correctly_classified = {
            **tool_payload,
            "risk": "critical",
            "reversibility": "irreversible",
            "data_class": "sensitive",
        }
        status, gated = post(
            endpoint,
            operation="tools.execute",
            payload=correctly_classified,
            token=AUTHORIZED_TOKEN,
            idempotency_key=f"test-critical-execution-{uuid4()}",
        )
        assert_status(status, 200, "critical action without approval", gated)
        execution = gated.get("payload", {})
        assert execution.get("state") == "waiting_approval", (
            f"critical action did not fail closed into approval state: {gated}"
        )
        assert execution.get("error_code") == ExecutionErrorCode.APPROVAL_REQUIRED.value
        assert execution.get("output") is None, "critical action produced output before approval"

        # Evidence remains tenant-scoped and the reference boundary emits a
        # concrete audit trail for the created run.
        status, run_events = post(
            endpoint,
            operation="runs.events",
            payload={"run_id": run_id},
        )
        assert_status(status, 200, "run event retrieval", run_events)
        assert run_events.get("payload", {}).get("events")
        status, run_evidence = post(
            endpoint,
            operation="runs.evidence",
            payload={"run_id": run_id},
        )
        assert_status(status, 200, "run evidence retrieval", run_evidence)
        assert "evidence" in run_evidence.get("payload", {})

        print(json.dumps({
            "status": "pass",
            "scope": "reference-platform",
            "checks": [
                "invalid-token", "forged-tenant", "forged-subject", "api-version",
                "traceparent", "content-type", "request-size", "idempotency",
                "tenant-isolation", "approval-authority", "registered-risk-floor",
                "critical-approval-gate", "run-events", "evidence-boundary",
            ],
            "production_status": "unverified",
        }, sort_keys=True))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
