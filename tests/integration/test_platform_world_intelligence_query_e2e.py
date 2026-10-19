from __future__ import annotations

import os
import re
import threading
import time
import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest


def test_platform_query_adapter_uses_signed_identity_and_postgres_policy_end_to_end() -> None:
    database_url = os.environ.get("WORLD_INTELLIGENCE_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("canonical gate supplies migrated PostgreSQL for the paired E2E")

    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from psycopg_pool import ConnectionPool
    from tinlance_agent_platform_api.service import APIRequest, APIResponse
    from tinlance_agent_platform_app.world_intelligence_api_handler import (
        WorldIntelligenceAPIHandler,
    )
    from tinlance_agent_platform_contracts import Principal
    from tinlance_agent_platform_mcp import (
        MCPToolGateway,
        WorldIntelligenceHTTPTransport,
        register_world_intelligence_tools,
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
    request_id = "platform-wi-query-" + uuid.uuid4().hex

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

    class Delegate:
        def handle(self, request: APIRequest) -> APIResponse:
            return APIResponse("success", {"delegated": request.operation})

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

    transport = WorldIntelligenceHTTPTransport(
        base_url=f"http://127.0.0.1:{server.server_address[1]}",
        audience=audience,
        token_issuer=TestPlatformTokenIssuer(),
        timeout_seconds=5,
        allow_loopback_http=True,
    )
    gateway = MCPToolGateway(transport)
    register_world_intelligence_tools(gateway)
    handler = WorldIntelligenceAPIHandler(
        delegate=Delegate(),
        gateway=gateway,
        environment="test",
    )

    def query(tenant: str, *, purpose: str = "account_research") -> APIResponse:
        principal = Principal(
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
        return handler.handle(
            APIRequest(
                tenant_id=tenant,
                subject_id=subject_id,
                operation="world_intelligence.query_regions",
                payload={"purpose": purpose, "limit": 100, "cursor": 0},
                request_id=request_id + "-" + tenant[-8:],
                trace_id=uuid.uuid4().hex,
                authenticated_principal=principal,
            )
        )

    try:
        allowed = query(tenant_id)
        assert allowed.status == "success", allowed.payload
        assert any(item.get("name") == region_name for item in allowed.payload["items"])

        denied = query(denied_tenant_id)
        assert denied.status == "denied", denied.payload
        assert denied.payload.get("error") == "world_intelligence_downstream_auth_failed"

        with pytest.raises(PermissionError, match="not authorized for the requested purpose"):
            query(tenant_id, purpose="marketing")
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
    allowed_request_id = request_id + "-" + tenant_id[-8:]
    denied_request_id = request_id + "-" + denied_tenant_id[-8:]
    assert any(
        row[0] == tenant_id
        and row[1] == "allowed"
        and row[2] == allowed_request_id
        and isinstance(row[3], str)
        and re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-01", row[3])
        for row in outcomes
    )
    assert any(
        row[0] == denied_tenant_id
        and row[1] == "denied"
        and row[2] == denied_request_id
        and isinstance(row[3], str)
        and re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-01", row[3])
        for row in outcomes
    )
