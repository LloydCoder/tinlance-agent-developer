#!/usr/bin/env python3
"""Cross-repository P6 routing conformance against the pinned TSIC authority contract."""
from __future__ import annotations

import json
from pathlib import Path

from tinlance_agent_platform_models import ModelRoute, ModelRouter, ModelRoutingRequest

TSIC = Path("/tmp/tinlance-tsic")
CONTRACT = TSIC / "contracts/models/routing-authority.json"
TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"


def main() -> None:
    if not CONTRACT.is_file():
        raise SystemExit("FAIL P6: pinned TSIC routing authority contract is missing")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required_inputs = {
        "task_policy",
        "risk_class",
        "model_capability",
        "data_classification",
        "budget",
        "availability",
    }
    required_outputs = {"model_id", "provider", "route", "policy_version"}
    rules = contract.get("rules", {})
    if contract.get("authority") != "agent-platform":
        raise SystemExit("FAIL P6: TSIC must assign routing authority to Agent Platform")
    if not required_inputs.issubset(set(contract.get("decision_inputs", []))):
        raise SystemExit("FAIL P6: TSIC routing inputs omit a canonical policy dimension")
    if not required_outputs.issubset(set(contract.get("decision_outputs", []))):
        raise SystemExit("FAIL P6: TSIC routing outputs omit a canonical decision field")
    if rules.get("no_local_unregistered_router") is not True:
        raise SystemExit("FAIL P6: TSIC must prohibit local unregistered routing")
    if rules.get("route_must_be_recorded") is not True:
        raise SystemExit("FAIL P6: TSIC must require recorded route decisions")
    if rules.get("budget_enforced_by_platform") is not True:
        raise SystemExit("FAIL P6: TSIC must keep budget enforcement in Platform")

    recorded = []
    router = ModelRouter(
        recorded.append,
        lambda candidate: candidate.route_id == "route-enterprise-safe",
        lambda _request: True,
    )
    router.register(
        ModelRoute(
            route_id="route-enterprise-safe",
            provider="provider-a",
            model="model-a",
            policy_version="tsic-routing-contract-1.0.0",
            capabilities=frozenset({"summarization"}),
            task_policies=frozenset({"summarization-policy-v1"}),
            data_classifications=frozenset({"public", "internal", "confidential"}),
            risk_classes=frozenset({"low", "moderate"}),
            max_cost_microusd=100,
            priority=10,
            tenants=frozenset({"tenant-a"}),
            agents=frozenset({"agent-a"}),
        )
    )
    request = ModelRoutingRequest(
        tenant_id="tenant-a",
        agent_id="agent-a",
        task_policy="summarization-policy-v1",
        model_capability="summarization",
        risk_class="moderate",
        data_classification="confidential",
        estimated_cost_microusd=50,
        available_budget_microusd=100,
        provider_availability=frozenset({"provider-a"}),
        trace_id=TRACE_ID,
    )
    allowed = router.route(request)
    if not allowed.allowed or allowed.route != "route-enterprise-safe":
        raise SystemExit("FAIL P6: eligible request did not select the registered route")
    if allowed.provider != "provider-a" or allowed.model_id != "model-a":
        raise SystemExit("FAIL P6: route decision disagrees with registered provider/model")
    if allowed.policy_version != "tsic-routing-contract-1.0.0" or allowed.trace_id != TRACE_ID:
        raise SystemExit("FAIL P6: decision evidence lost policy or trace context")
    if not recorded or recorded[-1] != allowed:
        raise SystemExit("FAIL P6: routing decision was returned before evidence recording")

    denied = router.route(
        ModelRoutingRequest(
            tenant_id="tenant-b",
            agent_id="agent-a",
            task_policy="summarization-policy-v1",
            model_capability="summarization",
            risk_class="moderate",
            data_classification="confidential",
            estimated_cost_microusd=50,
            available_budget_microusd=100,
            provider_availability=frozenset({"provider-a"}),
            trace_id=TRACE_ID,
        )
    )
    if denied.allowed or denied.route is not None or denied.reason_code != "no_eligible_route":
        raise SystemExit("FAIL P6: cross-tenant route selection did not fail closed")

    def unavailable_audit(_decision: object) -> None:
        raise OSError("evidence store unavailable")

    fail_closed = ModelRouter(
        unavailable_audit,
        lambda candidate: candidate.route_id == "route-audit-failure",
        lambda _request: True,
    )
    fail_closed.register(
        ModelRoute(
            route_id="route-audit-failure",
            provider="provider-a",
            model="model-a",
            policy_version="tsic-routing-contract-1.0.0",
            capabilities=frozenset({"summarization"}),
            task_policies=frozenset({"summarization-policy-v1"}),
            data_classifications=frozenset({"confidential"}),
            risk_classes=frozenset({"low", "moderate"}),
            max_cost_microusd=100,
        )
    )
    try:
        fail_closed.route(request)
    except RuntimeError as exc:
        if "failing closed" not in str(exc):
            raise SystemExit("FAIL P6: evidence outage did not fail closed with a stable error")
    else:
        raise SystemExit("FAIL P6: route was returned while evidence recording was unavailable")


    untrusted = ModelRouter(
        recorded.append,
        lambda candidate: candidate.route_id == "route-untrusted-context",
        lambda _request: False,
    )
    untrusted.register(
        ModelRoute(
            route_id="route-untrusted-context",
            provider="provider-a",
            model="model-a",
            policy_version="tsic-routing-contract-1.0.0",
            capabilities=frozenset({"summarization"}),
            task_policies=frozenset({"summarization-policy-v1"}),
            data_classifications=frozenset({"confidential"}),
            risk_classes=frozenset({"moderate"}),
            max_cost_microusd=100,
        )
    )
    untrusted_decision = untrusted.route(request)
    if untrusted_decision.allowed or untrusted_decision.reason_code != "untrusted_routing_context":
        raise SystemExit("FAIL P6: untrusted policy context did not fail closed")

    print(json.dumps({"phase": "P6", "scope": "model-routing-authority", "status": "pass"}))


if __name__ == "__main__":
    main()
