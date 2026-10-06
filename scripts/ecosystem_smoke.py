"""Cross-repository smoke test for the Tinlance agent stack.

This test exercises the real wire contract using the Platform reference HTTP
boundary, the official Platform SDK, and the Agent OS HTTP adapter. It does
not claim production infrastructure; it proves that the four repositories
agree on the versioned contract and authority boundary.
"""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from tinlance_agent_platform_api.http import serve
from tinlance_agent_platform_api.service import (
    APIResponse,
    AgentPlatformAPI,
    APIRequest,
)
from tinlance_agent_platform_sdk.client import AgentPlatform
from tinlance_agent_os.platform_adapter import AgentPlatformAdapter
from tinlance_agent_os.transport import (
    HttpPlatformTransport,
    PlatformRequestContext,
    StaticAccessTokenProvider,
)


ROOT = Path(__file__).resolve().parents[1]
TENANT = "tenant-a"
SUBJECT = "user-1"
AGENT_ID = uuid4()
TASK_ID = uuid4()
RUN_ID = uuid4()


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject_id: str


class Resolver:
    def resolve(self, bearer_token: str) -> Principal:
        assert bearer_token == "integration-token"
        return Principal(TENANT, SUBJECT)


class Handler:
    def handle(self, request: APIRequest) -> APIResponse:
        if request.operation == "health":
            return APIResponse("ok", {"ready": True})
        if request.operation == "principal.get":
            return APIResponse("ok", {"user_id": SUBJECT})
        if request.operation == "agents.list":
            return APIResponse(
                "ok",
                {"agents": [{"agent_id": str(AGENT_ID), "name": "integration-agent", "version": "1.0"}]},
            )
        if request.operation == "capabilities.list":
            return APIResponse("ok", {"capabilities": [{"capability_id": "research.read"}]})
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
                            "occurred_at": datetime.now(UTC).isoformat(),
                            "request_id": request.request_id,
                            "correlation_id": request.request_id,
                            "workspace_id": "workspace-1",
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


def main() -> None:
    # TADL gate: validate a canonical developer artifact before crossing the OS boundary.
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
        raise SystemExit(f"TADL validation failed:\n{result.stdout}\n{result.stderr}")

    platform = AgentPlatformAPI(Handler())
    server = serve(platform, Resolver(), host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f"http://127.0.0.1:{server.server_port}"
        sdk = AgentPlatform(
            base_url=endpoint,
            bearer_token="integration-token",
            tenant_id=TENANT,
            subject_id=SUBJECT,
            allow_insecure_http=True,
        )
        assert sdk.health().ready is True
        assert sdk.principal.get().user_id == SUBJECT
        assert sdk.agents.list()[0].agent_id == AGENT_ID
        run = sdk.runs.create(TASK_ID, AGENT_ID, "integration smoke test")
        assert run.run_id == RUN_ID
        assert sdk.runs.events(RUN_ID)
        assert sdk.runs.evidence(RUN_ID)

        os_transport = HttpPlatformTransport(
            endpoint=f"{endpoint}/v1/agent-platform",
            token_provider=StaticAccessTokenProvider("integration-token"),
            allow_insecure_localhost=True,
        )
        adapter = AgentPlatformAdapter(
            transport=os_transport,
            context=PlatformRequestContext(
                tenant_id=TENANT,
                subject_id=SUBJECT,
                request_id="os-integration-request",
            ),
        )
        assert adapter.health() is True
        assert adapter.get_principal().user_id == SUBJECT
        assert adapter.create_run(
            task_id=str(TASK_ID),
            agent_id=str(AGENT_ID),
            intent="OS adapter integration test",
            idempotency_key="os-integration-run",
        ).run_id == str(RUN_ID)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
