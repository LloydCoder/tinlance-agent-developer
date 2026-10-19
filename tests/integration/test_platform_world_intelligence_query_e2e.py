from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
import uuid
from http.client import HTTPConnection
from types import SimpleNamespace
from unittest.mock import patch

import pytest


def test_platform_mcp_to_world_intelligence_signed_query_and_postgres_policy() -> None:
    database_url = os.environ.get("WORLD_INTELLIGENCE_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("canonical gate supplies migrated PostgreSQL for the paired E2E")

    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from psycopg_pool import ConnectionPool
    from tinlance_agent_platform_api.service import APIResponse
    from tinlance_agent_platform_app.world_intelligence_api_handler import (
        WorldIntelligenceAPIHandler,
        WorldIntelligenceMCPDispatcher,
    )
    from tinlance_agent_platform_contracts import Principal
    from tinlance_agent_platform_mcp import (
        MCPProtocolService,
        MCPToolGateway,
        WorldIntelligenceHTTPTransport,
        register_world_intelligence_tools,
        with_world_intelligence_tools,
    )
    from runtime.config import RuntimeConfig
    from runtime.server import WorldIntelligenceServer

    issuer = "https://identity.tinlance.test"
    audience = "world-intelligence"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    tenant_id = "tenant-wi-query-" + uuid.uuid4().hex
    denied_tenant_id = "tenant-wi-query-denied-" + uuid.uuid4().hex
    subject_id = "agent-wi-query-" + uuid.uuid4().hex
    region_name = "region-platform-e2e-" + uuid.uuid4().hex
    trace_ids: dict[str, str] = {}
    parent_spans: dict[str, str] = {}

    with ConnectionPool(database_url, min_size=1, max_size=2, open=True) as pool:
        with pool.connection() as connection:
            connection.execute(
                "INSERT INTO world_intelligence.tenant_policies "
                "(tenant_id, allowed_capabilities, allowed_purposes) "
                "VALUES (%s, %s::jsonb, %s::jsonb)",
                (tenant_id, '["query_region"]', '["account_research"]'),
            )
            connection.execute(
                "INSERT INTO world_intelligence.geofences (name, geom) "
                "VALUES (%s, ST_GeomFromText(%s, 4326))",
                (region_name, "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"),
            )

    class FakeJWKClient:
        key = private_key.public_key()

        def __init__(self, *_args, **_kwargs):
            pass

        def get_signing_key_from_jwt(self, _token):
            return SimpleNamespace(key=self.key)

    class TestPlatformTokenIssuer:
        def issue_token(
            self,
            *,
            tenant_id: str,
            subject_id: str,
            audience: str,
            scopes: frozenset[str],
            purpose: str,
            request_id: str,
            traceparent: str | None,
            expires_in_seconds: int,
        ) -> str:
            now = int(time.time())
            claims = {
                "iss": issuer,
                "aud": audience,
                "sub": subject_id,
                "client_id": "tinlance-agent-platform-e2e",
                "jti": uuid.uuid4().hex,
                "principal_type": "agent",
                "tenant_id": tenant_id,
                "scope": " ".join(sorted(scopes)),
                "purpose": purpose,
                "request_id": request_id,
                "traceparent": traceparent,
                "iat": now,
                "exp": now + expires_in_seconds,
            }
            return jwt.encode(
                claims,
                private_key,
                algorithm="RS256",
                headers={"typ": "at+jwt", "kid": "e2e-platform-key"},
            )

    class APIHandlerDelegate:
        def handle(self, _request):
            return APIResponse("success", {"delegated": True})

    class ExistingMCPDispatcher:
        def dispatch(self, _request):
            return APIResponse("success", {"delegated": True})

    class Resolver:
        def resolve(self, token: str) -> Principal:
            if token == "allowed-user-token":
                tenant = tenant_id
            elif token == "denied-user-token":
                tenant = denied_tenant_id
            else:
                raise PermissionError("invalid test principal")
            return Principal(
                subject_id=subject_id,
                principal_type="agent",
                tenant_id=tenant,
                scopes=frozenset(
                    {
                        "world-intelligence.query_region",
                        "world-intelligence:purpose:account_research",
                    }
                ),
            )

    class RateLimiter:
        def allow(self, _tenant_id, _subject_id):
            return True

    config = RuntimeConfig(
        host="127.0.0.1",
        port=0,
        bearer_token=None,
        require_auth=True,
        storage_mode="postgres",
        database_url=database_url,
        platform_issuer=issuer,
        platform_audience=audience,
        platform_jwks_url=jwks_url,
    )
    with patch("runtime.platform_token.jwt.PyJWKClient", FakeJWKClient):
        server = WorldIntelligenceServer(("127.0.0.1", 0), config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        for _ in range(40):
            connection = HTTPConnection(
                "127.0.0.1", server.server_address[1], timeout=1
            )
            try:
                connection.request("GET", "/healthz")
                health = connection.getresponse()
                health.read()
                if health.status == 200:
                    break
            except OSError:
                time.sleep(0.05)
            finally:
                connection.close()
        else:
            raise AssertionError("World Intelligence HTTP runtime did not become healthy")

        transport = WorldIntelligenceHTTPTransport(
            base_url=f"http://127.0.0.1:{server.server_address[1]}",
            audience=audience,
            token_issuer=TestPlatformTokenIssuer(),
            timeout_seconds=5,
            allow_loopback_http=True,
        )
        gateway = MCPToolGateway(transport)
        register_world_intelligence_tools(gateway)
        api_handler = WorldIntelligenceAPIHandler(
            delegate=APIHandlerDelegate(),
            gateway=gateway,
            environment="test",
        )
        dispatcher = WorldIntelligenceMCPDispatcher(
            delegate=ExistingMCPDispatcher(),
            handler=api_handler,
        )
        service = MCPProtocolService(
            dispatcher,
            Resolver(),
            with_world_intelligence_tools(()),
            allowed_origins=(),
            rate_limiter=RateLimiter(),
        )
        meta = {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientInfo": {
                "name": "tinlance-world-intelligence-e2e",
                "version": "1.0.0",
            },
            "io.modelcontextprotocol/clientCapabilities": {},
        }

        listed = service.handle(
            {
                "content-type": "application/json",
                "authorization": "Bearer allowed-user-token",
                "mcp-protocol-version": "2026-07-28",
                "mcp-method": "tools/list",
            },
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "list-world-intelligence",
                    "method": "tools/list",
                    "params": {"_meta": meta},
                }
            ).encode(),
        )
        listed_payload = json.loads(listed.body)
        names = {tool["name"] for tool in listed_payload["result"]["tools"]}
        assert "world_intelligence_query_regions" in names
        region_tool = next(
            tool
            for tool in listed_payload["result"]["tools"]
            if tool["name"] == "world_intelligence_query_regions"
        )
        assert region_tool["annotations"]["readOnlyHint"] is True
        assert region_tool["annotations"]["destructiveHint"] is False

        def query(token: str, tenant: str) -> tuple[dict, dict, str]:
            trace_id = uuid.uuid4().hex
            parent_span = uuid.uuid4().hex[:16]
            traceparent = f"00-{trace_id}-{parent_span}-01"
            trace_ids[tenant] = trace_id
            parent_spans[tenant] = parent_span
            rpc_id = "query-" + tenant[-8:]
            response = service.handle(
                {
                    "content-type": "application/json",
                    "authorization": f"Bearer {token}",
                    "mcp-protocol-version": "2026-07-28",
                    "mcp-method": "tools/call",
                    "mcp-name": "world_intelligence_query_regions",
                    "traceparent": traceparent,
                },
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "method": "tools/call",
                        "params": {
                            "_meta": meta,
                            "name": "world_intelligence_query_regions",
                            "arguments": {
                                "purpose": "account_research",
                                "limit": 100,
                                "cursor": 0,
                            },
                        },
                    }
                ).encode(),
            )
            assert response.status_code == 200
            envelope = json.loads(response.body)
            result = envelope["result"]
            text_payload = json.loads(result["content"][0]["text"])
            fingerprint = hashlib.sha256(
                f"{tenant}:{subject_id}:{rpc_id}".encode()
            ).hexdigest()[:32]
            expected_request_id = f"mcp-{fingerprint}"
            return result, text_payload, expected_request_id

        allowed_result, allowed_payload, allowed_request_id = query(
            "allowed-user-token", tenant_id
        )
        assert allowed_result["isError"] is False
        assert allowed_payload["status"] == "success", allowed_payload
        assert any(
            item.get("name") == region_name for item in allowed_payload["payload"]["items"]
        )

        denied_result, denied_payload, denied_request_id = query(
            "denied-user-token", denied_tenant_id
        )
        assert denied_result["isError"] is True
        assert denied_payload["status"] == "denied", denied_payload
        assert (
            denied_payload["payload"].get("error")
            == "world_intelligence_downstream_auth_failed"
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    with ConnectionPool(database_url, min_size=1, max_size=2, open=True) as pool:
        with pool.connection() as connection:
            outcomes = connection.execute(
                "SELECT tenant_id, outcome, metadata->>'request_id', metadata->>'traceparent' "
                "FROM world_intelligence.security_audit_events "
                "WHERE tenant_id = ANY(%s) ORDER BY occurred_at",
                ([tenant_id, denied_tenant_id],),
            ).fetchall()

    for tenant, outcome, expected_request_id in (
        (tenant_id, "allowed", allowed_request_id),
        (denied_tenant_id, "denied", denied_request_id),
    ):
        assert any(
            row[0] == tenant
            and row[1] == outcome
            and row[2] == expected_request_id
            and isinstance(row[3], str)
            and re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-01", row[3])
            and row[3].split("-")[1] == trace_ids[tenant]
            and row[3].split("-")[2] != parent_spans[tenant]
            for row in outcomes
        )
