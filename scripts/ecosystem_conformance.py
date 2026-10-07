"""Executable conformance suite for the Tinlance Agent Ecosystem.

The suite is intentionally cross-repository: it materializes the exact revisions
from ecosystem.lock.json, validates the TADL artifact boundary, exercises the
Platform reference HTTP contract through both the official SDK and Agent OS,
and asserts security/authority invariants at the wire and import boundaries.

This is a contract/conformance gate, not a production-infrastructure test.
"""

from __future__ import annotations

import json
import subprocess
import threading
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from tinlance_agent_platform_api.http import serve
from tinlance_agent_platform_api.service import APIRequest, APIResponse, AgentPlatformAPI
from tinlance_agent_platform_sdk.client import AgentPlatform, API_VERSION, GOVERNED_EXECUTION_CONTRACT
from tinlance_agent_os.platform_adapter import AgentPlatformAdapter
from tinlance_agent_os.transport import (
    HttpPlatformTransport,
    PlatformRequestContext,
    StaticAccessTokenProvider,
)


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "ecosystem.lock.json"
TENANT = "tenant-conformance"
SUBJECT = "subject-conformance"
TOKEN = "conformance-token"
AGENT_ID = UUID("00000000-0000-0000-0000-000000000101")
TASK_ID = UUID("00000000-0000-0000-0000-000000000102")
RUN_ID = UUID("00000000-0000-0000-0000-000000000103")


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject_id: str


class Resolver:
    def resolve(self, bearer_token: str) -> Principal:
        if bearer_token != TOKEN:
            raise PermissionError("unknown token")
        return Principal(TENANT, SUBJECT)


class Handler:
    def __init__(self) -> None:
        self.calls: Counter[str] = Counter()
        self.requests: list[APIRequest] = []

    def handle(self, request: APIRequest) -> APIResponse:
        self.calls[request.operation] += 1
        self.requests.append(request)
        if request.operation == "health":
            return APIResponse("ok", {"ready": True})
        if request.operation == "principal.get":
            return APIResponse("ok", {"user_id": SUBJECT})
        if request.operation == "agents.list":
            return APIResponse(
                "ok",
                {
                    "agents": [
                        {
                            "agent_id": str(AGENT_ID),
                            "name": "conformance-agent",
                            "version": "1.0",
                        }
                    ]
                },
            )
        if request.operation == "capabilities.list":
            return APIResponse(
                "ok",
                {"capabilities": [{"capability_id": "research.read", "version": "1"}]},
            )
        if request.operation == "runs.create":
            return APIResponse(
                "accepted",
                {
                    "run_id": str(RUN_ID),
                    "task_id": str(TASK_ID),
                    "agent_id": str(AGENT_ID),
                    "state": "running",
                },
            )
        if request.operation == "runs.events":
            return APIResponse(
                "ok",
                {
                    "events": [
                        {
                            "event_id": str(uuid4()),
                            "event_type": "run.started",
                            "occurred_at": "2026-01-01T00:00:00+00:00",
                            "request_id": request.request_id,
                            "correlation_id": request.request_id,
                            "workspace_id": "workspace-conformance",
                            "task_id": str(TASK_ID),
                            "agent_id": str(AGENT_ID),
                            "platform_run_id": str(RUN_ID),
                            "payload": {},
                        }
                    ]
                },
            )
        if request.operation == "runs.evidence":
            return APIResponse("ok", {"evidence": [{"evidence_id": str(uuid4())}]})
        raise AssertionError(f"unexpected operation: {request.operation}")


def assert_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_raises(expected: type[BaseException], fn, message: str) -> None:
    try:
        fn()
    except expected:
        return
    raise AssertionError(message)


def post_raw(
    endpoint: str,
    *,
    tenant_id: str,
    subject_id: str,
    operation: str,
    payload: dict[str, object],
    token: str = TOKEN,
    api_version: str = API_VERSION,
    request_id: str = "conformance-request",
    idempotency_key: str | None = None,
    traceparent: str | None = None,
) -> tuple[int, dict[str, object]]:
    body = json.dumps(
        {
            "tenant_id": tenant_id,
            "subject_id": subject_id,
            "operation": operation,
            "payload": payload,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tinlance-API-Version": api_version,
        "X-Request-ID": request_id,
    }
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    if traceparent is not None:
        headers["traceparent"] = traceparent
    target = endpoint.rstrip("/") + "/v1/agent-platform"
    request = urllib.request.Request(
        target,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def validate_tadl() -> None:
    result = subprocess.run(
        [
            "node",
            "cli/tadl.mjs",
            "validate",
            "capability/v1/capability.schema.json",
            "schemas/examples/security-assessment.capability.json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"TADL artifact validation failed:\n{result.stdout}\n{result.stderr}")


def validate_lock() -> dict[str, object]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    assert_equal(lock["schema"], "tinlance-agent-ecosystem-lock/v1", "lock schema")
    assert_equal(lock["contracts"]["platform_api"], API_VERSION, "Platform API version")
    assert_equal(
        lock["contracts"]["governed_execution"],
        GOVERNED_EXECUTION_CONTRACT,
        "governed execution contract",
    )
    assert_equal(lock["contracts"]["endpoint"], "POST /v1/agent-platform", "wire endpoint")
    for name, item in lock["repositories"].items():
        if not item.get("repository") or not item.get("ref"):
            raise AssertionError(f"repository lock entry {name!r} is incomplete")
        if len(item["ref"]) != 40:
            raise AssertionError(f"repository lock entry {name!r} is not a full commit SHA")
    return lock


def validate_budget_governance_reconciliation() -> None:
    """Require the locked four-repository stack to expose one budget authority boundary."""
    platform_doc = Path("/tmp/tinlance-platform/docs/production-runtime/M13-4-BUDGET-RESOURCE-GOVERNANCE.md")
    required_docs = (
        platform_doc,
        Path("/tmp/tinlance-platform_sdk/docs/integration/ECOSYSTEM.md"),
        Path("/tmp/tinlance-os/docs/integration/ECOSYSTEM.md"),
        ROOT / "docs/integration/ECOSYSTEM.md",
    )
    for path in required_docs:
        if not path.exists():
            raise AssertionError(f"budget governance reconciliation document is missing: {path}")
        content = path.read_text(encoding="utf-8")
        if path == platform_doc:
            if "tenant, agent, run, action and resource" not in content:
                raise AssertionError("Platform budget scope invariant is not documented")
        elif "Budget governance boundary" not in content:
            raise AssertionError(f"budget authority boundary is not reconciled: {path}")


def validate_tool_authority_reconciliation() -> None:
    """Require the locked stack to expose one consequential tool and sandbox authority boundary."""
    required = {
        Path("/tmp/tinlance-platform/docs/production-runtime/M13-5-SANDBOX-TOOL-MCP-AUTHORITY.md"):
            "tenant/run/tool/action/resource",
        Path("/tmp/tinlance-platform_sdk/docs/integration/ECOSYSTEM.md"):
            "M13.5 tool authority reconciliation",
        Path("/tmp/tinlance-os/docs/integration/ECOSYSTEM.md"):
            "M13.5 tool authority reconciliation",
        ROOT / "docs/integration/ECOSYSTEM.md":
            "Platform-issued",
    }
    for path, marker in required.items():
        if not path.exists():
            raise AssertionError(f"tool authority reconciliation document is missing: {path}")
        if marker not in path.read_text(encoding="utf-8"):
            raise AssertionError(f"tool authority marker missing from {path}: {marker}")


def validate_production_runtime_reconciliation() -> None:
    """Require M13.6-M13.8 authority boundaries across the locked stack."""
    required = {
        Path("/tmp/tinlance-platform/docs/production-runtime/M13-6-SECRETS-CREDENTIAL-GOVERNANCE.md"): (
            "Purpose + audience + time validation",
        ),
        Path("/tmp/tinlance-platform/docs/production-runtime/M13-7-EVIDENCE-AUDIT-NONREPUDIATION.md"): (
            "Non-Repudiation",
        ),
        Path("/tmp/tinlance-platform/docs/production-runtime/M13-8-OBSERVABILITY-INCIDENT-CORRELATION.md"): (
            "Incident correlation",
        ),
        Path("/tmp/tinlance-platform_sdk/docs/integration/ECOSYSTEM.md"): (
            "M13.6 — Secrets and credential governance",
            "M13.7 — Evidence, audit and non-repudiation",
            "M13.8 — Observability and incident correlation",
            "Final M13.4-M13.8 authority reconciliation",
        ),
        Path("/tmp/tinlance-os/docs/integration/ECOSYSTEM.md"): (
            "M13.6 — Secrets and credential governance",
            "M13.7 — Evidence, audit and non-repudiation",
            "M13.8 — Observability and incident correlation",
            "Final M13.4-M13.8 authority reconciliation",
        ),
        ROOT / "docs/integration/ECOSYSTEM.md": (
            "M13.6 — Secrets and credential governance",
            "M13.7 — Evidence, audit and non-repudiation",
            "M13.8 — Observability and incident correlation",
            "Final M13.4-M13.8 authority reconciliation",
        ),
    }
    for path, markers in required.items():
        if not path.exists():
            raise AssertionError(f"production runtime document is missing: {path}")
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                raise AssertionError(f"production runtime marker missing from {path}: {marker}")


def validate_authority_boundaries(lock: dict[str, object]) -> None:
    """Reject accidental dependency inversion into the authority kernel."""
    roots = {
        # Only scan product source trees. The conformance harness intentionally
        # imports the other layers and therefore is not itself a dependency.
        "developer": ROOT / "cli",
        "os": Path("/tmp/tinlance-os/src"),
        "platform_sdk": Path("/tmp/tinlance-platform_sdk/src"),
        "platform": Path("/tmp/tinlance-platform/packages"),
    }
    forbidden = {
        "developer": ("tinlance_agent_platform_", "tinlance_agent_os"),
        "os": (
            "tinlance_agent_platform_authorization",
            "tinlance_agent_platform_policy",
            "tinlance_agent_platform_runtime",
            "tinlance_agent_platform_sandbox",
            "tinlance_agent_platform_secrets",
            "tinlance_agent_platform_evidence",
        ),
        "platform_sdk": ("tinlance_agent_platform_authorization", "tinlance_agent_platform_runtime"),
        "platform": ("tinlance_agent_os", "tinlance_agent_platform_sdk"),
    }
    for name, root in roots.items():
        if not root.exists():
            raise AssertionError(f"locked repository {name!r} was not materialized at {root}")
        for path in root.rglob("*.py"):
            if any(part in {".git", ".venv", "dist", "build"} for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden[name]:
                if f"import {token}" in text or f"from {token}" in text:
                    raise AssertionError(
                        f"authority boundary violation: {name} imports {token} in {path}"
                    )


def run_contract_checks() -> None:
    handler = Handler()
    api = AgentPlatformAPI(handler)
    server = serve(api, Resolver(), host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}"
    try:
        # SDK positive path.
        sdk = AgentPlatform(
            base_url=endpoint,
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            traceparent="00-11111111111111111111111111111111-2222222222222222-01",
            allow_insecure_http=True,
        )
        assert sdk.health().ready is True
        assert sdk.principal.get().user_id == SUBJECT
        assert sdk.agents.list()[0].agent_id == AGENT_ID
        assert sdk.capabilities.list(AGENT_ID)[0].capability_id == "research.read"
        run = sdk.runs.create(TASK_ID, AGENT_ID, "conformance run")
        assert_equal(run.run_id, RUN_ID, "SDK run ID")
        assert sdk.runs.events(RUN_ID)
        assert sdk.runs.evidence(RUN_ID)

        # OS uses the same versioned wire boundary.
        transport = HttpPlatformTransport(
            endpoint=f"{endpoint}/v1/agent-platform",
            token_provider=StaticAccessTokenProvider(TOKEN),
            allow_insecure_localhost=True,
        )
        adapter = AgentPlatformAdapter(
            transport=transport,
            context=PlatformRequestContext(
                tenant_id=TENANT,
                subject_id=SUBJECT,
                request_id="os-conformance-request",
            ),
        )
        assert adapter.health() is True
        assert adapter.get_principal().user_id == SUBJECT
        assert adapter.create_run(
            task_id=str(TASK_ID),
            agent_id=str(AGENT_ID),
            intent="OS conformance run",
            idempotency_key="os-conformance-idempotency",
        ).run_id == str(RUN_ID)

        # API version negotiation is fail-closed.
        status, body = post_raw(
            endpoint,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            operation="health",
            payload={},
            api_version="0.9",
            request_id="bad-version",
        )
        assert_equal(status, 426, "unsupported API version status")
        assert_equal(body["error"], "api_version_required", "unsupported API version error")

        # Authenticated principal binding prevents cross-tenant/subject confusion.
        status, body = post_raw(
            endpoint,
            tenant_id="attacker-tenant",
            subject_id=SUBJECT,
            operation="health",
            payload={},
            request_id="wrong-tenant",
        )
        assert_equal(status, 403, "principal mismatch status")
        assert_equal(body["error"], "forbidden", "principal mismatch error")

        # Consequential requests are idempotent and conflict on changed payloads.
        first_status, first_body = post_raw(
            endpoint,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            operation="runs.create",
            payload={"task_id": str(TASK_ID), "agent_id": str(AGENT_ID), "intent": "same"},
            request_id="idem-one",
            idempotency_key="idem-one",
        )
        second_status, second_body = post_raw(
            endpoint,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            operation="runs.create",
            payload={"task_id": str(TASK_ID), "agent_id": str(AGENT_ID), "intent": "same"},
            request_id="idem-two",
            idempotency_key="idem-one",
        )
        conflict_status, conflict_body = post_raw(
            endpoint,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            operation="runs.create",
            payload={"task_id": str(TASK_ID), "agent_id": str(AGENT_ID), "intent": "different"},
            request_id="idem-three",
            idempotency_key="idem-one",
        )
        assert_equal(first_status, 200, "first idempotent request")
        assert_equal(second_status, 200, "idempotent replay")
        assert_equal(second_body, first_body, "idempotent replay body")
        assert_equal(conflict_status, 409, "idempotency conflict status")
        assert_equal(conflict_body["error"], "IDEMPOTENCY_CONFLICT", "idempotency conflict error")

        # SDK and OS must propagate the version and trace/idempotency metadata.
        if not handler.requests:
            raise AssertionError("no Platform requests were observed")
        assert any(req.trace_id for req in handler.requests), "trace context was not propagated"
        assert any(
            req.operation == "runs.create" and req.idempotency_key
            for req in handler.requests
        ), "consequential idempotency metadata was not propagated"

        # Transport security: insecure HTTP is permitted only for explicit localhost testing.
        assert_raises(
            ValueError,
            lambda: HttpPlatformTransport(
                endpoint="http://example.invalid/v1/agent-platform",
                token_provider=StaticAccessTokenProvider(TOKEN),
            ),
            "non-local HTTP transport was not rejected",
        )
        assert_raises(
            ValueError,
            lambda: AgentPlatform(
                base_url="http://example.invalid",
                bearer_token=TOKEN,
                tenant_id=TENANT,
                subject_id=SUBJECT,
            ),
            "SDK accepted non-HTTPS production transport",
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def main() -> None:
    lock = validate_lock()
    validate_tadl()
    validate_authority_boundaries(lock)
    validate_budget_governance_reconciliation()
    validate_tool_authority_reconciliation()
    validate_production_runtime_reconciliation()
    run_contract_checks()
    print("Tinlance Agent Ecosystem conformance: PASS")


if __name__ == "__main__":
    main()
