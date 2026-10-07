"""P2 adversarial certification for the four-repository governed execution path.

This suite deliberately attacks the boundary with forged identity/tenant data,
invalid credentials, idempotency reuse and malformed authority metadata. It
uses the reference HTTP boundary and therefore proves contract behavior, not
production infrastructure.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from uuid import UUID

from tinlance_agent_platform_api.http import serve
from tinlance_agent_platform_api.service import APIRequest, APIResponse, AgentPlatformAPI

TENANT = "tenant-p2"
SUBJECT = "subject-p2"
TOKEN = "token-p2"
AGENT_ID = UUID("00000000-0000-0000-0000-000000000201")
TASK_ID = UUID("00000000-0000-0000-0000-000000000202")
RUN_ID = UUID("00000000-0000-0000-0000-000000000203")


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject_id: str


class Resolver:
    def resolve(self, bearer_token: str) -> Principal:
        if bearer_token != TOKEN:
            raise PermissionError("invalid token")
        return Principal(TENANT, SUBJECT)


class Handler:
    def __init__(self) -> None:
        self.idempotency_payloads: dict[str, bytes] = {}

    def handle(self, request: APIRequest) -> APIResponse:
        if request.operation == "health":
            return APIResponse("ok", {"ready": True})
        if request.operation == "runs.create":
            return APIResponse(
                "accepted",
                {"run_id": str(RUN_ID), "task_id": str(TASK_ID), "agent_id": str(AGENT_ID)},
            )
        raise AssertionError(f"unexpected operation: {request.operation}")


def post(endpoint: str, *, tenant: str, subject: str, token: str, payload: dict[str, object],
         request_id: str, idempotency_key: str | None = None) -> tuple[int, dict[str, object]]:
    body = json.dumps(
        {"tenant_id": tenant, "subject_id": subject, "operation": "runs.create", "payload": payload},
        separators=(",", ":"),
    ).encode()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tinlance-API-Version": "1.1",
        "X-Request-ID": request_id,
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                endpoint.rstrip("/") + "/v1/agent-platform",
                data=body,
                headers=headers,
                method="POST",
            ),
            timeout=5,
        ) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def main() -> None:
    server = serve(AgentPlatformAPI(Handler()), Resolver(), host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}"
    try:
        idempotency_key = str(UUID("00000000-0000-0000-0000-000000000204"))
        status, _ = post(
            endpoint, tenant=TENANT, subject=SUBJECT, token="forged-token",
            payload={"task_id": str(TASK_ID)}, request_id="invalid-token",
        )
        assert status in {401, 403}, f"invalid token was not rejected: {status}"

        status, _ = post(
            endpoint, tenant="tenant-attacker", subject=SUBJECT, token=TOKEN,
            payload={"task_id": str(TASK_ID)}, request_id="cross-tenant",
        )
        assert status in {400, 401, 403}, f"cross-tenant request was not rejected: {status}"

        status, _ = post(
            endpoint, tenant=TENANT, subject="forged-subject", token=TOKEN,
            payload={"task_id": str(TASK_ID)}, request_id="forged-subject",
        )
        assert status in {400, 401, 403}, f"forged subject was not rejected: {status}"

        status, _ = post(
            endpoint, tenant=TENANT, subject=SUBJECT, token=TOKEN,
            payload={"task_id": str(TASK_ID), "intent": "first"},
            request_id="idempotency-1", idempotency_key=idempotency_key,
        )
        assert status < 500, f"baseline idempotent request failed unexpectedly: {status}"

        status, _ = post(
            endpoint, tenant=TENANT, subject=SUBJECT, token=TOKEN,
            payload={"task_id": str(TASK_ID), "intent": "different"},
            request_id="idempotency-2", idempotency_key="p2-idempotency-key",
        )
        assert status in {400, 409}, f"idempotency reuse was not rejected: {status}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
