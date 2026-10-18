#!/usr/bin/env python3
"""Exact-SHA P7 conformance for provider transport and execution-scoped credentials."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "ecosystem.lock.json").read_text(encoding="utf-8"))
PLATFORM = Path("/tmp/tinlance-platform")
TSIC = Path("/tmp/tinlance-tsic")
CONTRACT_PATH = TSIC / "contracts/models/provider-adapter-boundary.json"
SCHEMA_PATH = TSIC / "schemas/provider-adapter-boundary.schema.json"

FAILURES: list[str] = []


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    if not path.is_file():
        FAILURES.append(f"missing P7 implementation file: {path}")
        return
    source = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker not in source:
            FAILURES.append(f"{path.relative_to(PLATFORM)} is missing invariant marker {marker!r}")


def verify_exact_revision(root: Path, expected: str, label: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode or result.stdout.strip() != expected:
        FAILURES.append(
            f"{label} checkout is not the exact locked revision: "
            f"expected {expected}, got {result.stdout.strip() or result.stderr.strip()}"
        )


def run_pytest(cwd: Path, path: Path, label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(path)],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} regression tests failed:\n{result.stdout[-5000:]}\n{result.stderr[-3000:]}"
        )


def main() -> None:
    authority = LOCK["integration_authority"]
    platform_ref = LOCK["repositories"]["platform"]["ref"]
    verify_exact_revision(PLATFORM, platform_ref, "Platform")
    verify_exact_revision(TSIC, authority["ref"], "TSIC")

    if not SCHEMA_PATH.is_file() or not CONTRACT_PATH.is_file():
        raise SystemExit("FAIL P7: pinned TSIC provider-adapter schema/contract is missing")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)

    if contract.get("authority") != "agent-platform":
        FAILURES.append("TSIC provider-adapter contract must retain Platform authority")
    if contract.get("scope") != "canonical-ecosystem-p7":
        FAILURES.append("TSIC provider-adapter contract is not scoped to canonical P7")
    if contract.get("credentials", {}).get("persist") != "forbidden":
        FAILURES.append("TSIC contract must forbid credential persistence")
    if contract.get("privacy", {}).get("credential_in_exception_or_log") is not False:
        FAILURES.append("TSIC contract must forbid credential leakage in logs/exceptions")
    if contract.get("authority_invariants", {}).get("adapter_grants_authority") is not False:
        FAILURES.append("provider adapters must not grant execution authority")

    require_markers(
        PLATFORM / "packages/models/src/tinlance_agent_platform_models/gateway.py",
        (
            "principal_id: str | None",
            "execution_id: UUID | None",
            "capability_id: str | None",
            "execution-scoped model context must be complete",
        ),
    )
    require_markers(
        PLATFORM / "packages/secrets/src/tinlance_agent_platform_secrets/model_provider.py",
        (
            "class ScopedModelCredentialProvider",
            "request.tenant_id != self.handle.tenant_id",
            "request.principal_id != self.handle.principal_id",
            "request.agent_id != str(self.handle.agent_id)",
            "request.execution_id != self.handle.execution_id",
            "request.capability_id != self.handle.capability_id",
            "self.broker.resolve_for_execution(",
        ),
    )
    require_markers(
        PLATFORM / "packages/models/src/tinlance_agent_platform_models/openai_compatible.py",
        (
            "class ModelProviderError",
            "MAX_REQUEST_BYTES = 1 * 1024 * 1024",
            "DEFAULT_MAX_RESPONSE_BYTES = 4 * 1024 * 1024",
            "class _NoRedirectHandler",
            'headers["traceparent"] = request.traceparent',
        ),
    )

    run_pytest(
        TSIC,
        TSIC / "tests/test_provider_adapter_boundary.py",
        "TSIC provider-adapter contract",
    )
    run_pytest(
        PLATFORM,
        PLATFORM / "tests/unit/test_openai_compatible_provider.py",
        "Platform provider adapter and scoped credential",
    )

    if FAILURES:
        raise SystemExit("FAIL P7 adapter conformance:\n- " + "\n- ".join(FAILURES))
    print(
        "PASS P7: exact-SHA TSIC contract, bounded provider transport, and "
        "execution-scoped credentials conform"
    )


if __name__ == "__main__":
    main()
