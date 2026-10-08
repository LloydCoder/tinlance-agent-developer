#!/usr/bin/env python3
"""Verify TADL consumes the canonical TSIC ecosystem contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "ecosystem.lock.json").read_text(encoding="utf-8"))
TSIC_ROOT = Path("/tmp/tinlance-tsic")

EXPECTED_ROLE = "developer_validation_consumer"
REQUIRED_CONTRACTS = {
    "identity-context",
    "agent-registration",
    "delivery-semantics",
    "trace-context",
    "agent-interoperability-gate",
    "economic-attribution",
}


def main() -> None:
    authority = LOCK["integration_authority"]
    if authority["repository"] != "LloydCoder/tinlance-system-integration":
        raise AssertionError("TADL integration authority is not TSIC")
    if len(authority["ref"]) != 40:
        raise AssertionError("TSIC integration authority ref is not immutable")

    tsic_manifest = json.loads(
        (TSIC_ROOT / "manifests/ecosystem.json").read_text(encoding="utf-8")
    )
    tadl = next(item for item in tsic_manifest["systems"] if item["id"] == "agent-developer")
    if tadl["repository"] != "LloydCoder/tinlance-agent-developer":
        raise AssertionError("TSIC TADL repository mapping is stale")
    if tadl.get("governance_role") != EXPECTED_ROLE:
        raise AssertionError("TADL is not registered as a conformance consumer")

    adapter = json.loads(
        (TSIC_ROOT / "integrations/agent-developer/adapter.json").read_text(
            encoding="utf-8"
        )
    )
    if adapter["adapter_id"] != "tsic-agent-developer-reference":
        raise AssertionError("wrong TSIC TADL adapter")
    if adapter["authority"]["integration_contracts"] != "tsic":
        raise AssertionError("TADL cannot replace TSIC integration authority")
    if adapter["authority"]["execution_authority"] != "agent-platform":
        raise AssertionError("TADL cannot replace Platform execution authority")

    bindings = {item["tsic_contract"] for item in adapter["contract_bindings"]}
    if bindings != REQUIRED_CONTRACTS:
        raise AssertionError(
            f"TADL TSIC binding drift: expected {sorted(REQUIRED_CONTRACTS)}, "
            f"got {sorted(bindings)}"
        )

    invariants = set(adapter["invariants"])
    required_invariants = {
        "tadl_never_grants_execution_authority",
        "tadl_never_authorizes_side_effects",
        "tadl_is_not_ecosystem_integration_authority",
        "developer_validation_is_not_execution_authorization",
        "platform_remains_consequential_authority",
        "tsic_contracts_are_canonical",
    }
    if invariants != required_invariants:
        raise AssertionError("TADL TSIC authority invariants drifted")

    print(
        "PASS TADL TSIC conformance:",
        f"revision={authority['ref']} contracts={len(bindings)}",
    )


if __name__ == "__main__":
    main()
