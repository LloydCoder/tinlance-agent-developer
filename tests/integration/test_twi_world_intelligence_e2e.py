from __future__ import annotations

import hashlib
import threading
import uuid

from runtime.config import RuntimeConfig
from runtime.server import WorldIntelligenceServer
from tinlance_web_intelligence.integrations.world_intelligence.client import (
    WorldIntelligenceDeliveryError,
    WorldIntelligenceEvidenceClient,
)
from tinlance_web_intelligence.integrations.world_intelligence.outbox import OutboxEvent


def _payload() -> dict[str, str]:
    quote = "A verified source quote for cross-repository integration."
    return {
        "schema_version": "1.0.0",
        "source_system": "tinlance-web-intelligence",
        "tenant_ref": hashlib.sha256(b"twi-wi-e2e-tenant").hexdigest(),
        "source_job_id": "twi-wi-e2e-job",
        "claim_id": "twi-wi-e2e-claim",
        "statement": quote,
        "source_url": "https://example.com/source",
        "source_url_redacted": False,
        "retrieved_at": "2026-10-19T00:00:00+00:00",
        "media_type": "text/html",
        "artifact_sha256": hashlib.sha256(b"captured-artifact").hexdigest(),
        "quote": quote,
        "quote_sha256": hashlib.sha256(" ".join(quote.split()).encode()).hexdigest(),
        "verifier_version": "twi-citation-verifier/1.0.0",
        "report_sha256": hashlib.sha256(b"verified-report").hexdigest(),
    }


def _event(payload: dict[str, str], *, key: str) -> OutboxEvent:
    return OutboxEvent(
        event_id=str(uuid.uuid4()),
        tenant_ref=payload["tenant_ref"],
        subject_ref=hashlib.sha256(b"twi-wi-e2e-subject").hexdigest(),
        idempotency_key=key,
        payload=payload,
        status="delivering",
        attempts=1,
        lease_token="e2e-lease-token",
        request_id="twi-wi-e2e-request",
        traceparent="00-0123456789abcdef0123456789abcdef-0123456789abcdef-01",
    )


def test_twi_client_delivers_to_world_intelligence_http_intake_end_to_end() -> None:
    service_token = "test-world-intelligence-service-token-0123456789"
    config = RuntimeConfig(
        host="127.0.0.1",
        port=0,
        bearer_token="unused-query-token",
        source_evidence_bearer_token=service_token,
        require_auth=True,
        max_body_bytes=1024 * 1024,
    )
    server = WorldIntelligenceServer(("127.0.0.1", 0), config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = WorldIntelligenceEvidenceClient(
        f"http://127.0.0.1:{server.server_address[1]}",
        service_token,
        allow_http_for_development=True,
    )
    try:
        first_idempotency_key = "fixture-idempotency-case"
        event = _event(_payload(), key=first_idempotency_key)
        first_id = client.send(event)
        replay_id = client.send(event)
        assert first_id == replay_id
        assert str(uuid.UUID(first_id)) == first_id

        conflicting_payload = _payload()
        conflicting_payload["statement"] = "Conflicting payload for the same idempotency key."
        conflict = _event(conflicting_payload, key=event.idempotency_key)
        try:
            client.send(conflict)
        except WorldIntelligenceDeliveryError as exc:
            assert exc.error_code == "remote_idempotency_conflict"
            assert exc.retryable is False
        else:
            raise AssertionError("World Intelligence must reject conflicting idempotency replays")

        wrong_token_client = WorldIntelligenceEvidenceClient(
            f"http://127.0.0.1:{server.server_address[1]}",
            "wrong-world-intelligence-service-token-012345",
            allow_http_for_development=True,
        )
        try:
            try:
                unauthorized_idempotency = "fixture-unauthorized-case"
                wrong_token_client.send(_event(_payload(), key=unauthorized_idempotency))
            except WorldIntelligenceDeliveryError as exc:
                assert exc.error_code == "remote_rejected_source_evidence"
                assert exc.retryable is False
            else:
                raise AssertionError("World Intelligence must reject an invalid service credential")
        finally:
            wrong_token_client.close()
    finally:
        client.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
