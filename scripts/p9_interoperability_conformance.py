#!/usr/bin/env python3
"""Run P9 MCP/A2A adversarial tests against the exact locked ecosystem revisions."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = Path("/tmp/tinlance-platform")
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
TSIC = Path("/tmp/tinlance-tsic")
FAILURES: list[str] = []


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        FAILURES.append(f"cannot load {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        FAILURES.append(f"JSON root must be an object: {path}")
        return {}
    return value


def require_file(root: Path, relative: str, *markers: str) -> None:
    path = root / relative
    if not path.is_file():
        FAILURES.append(f"missing P9 artifact: {root.name}/{relative}")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker.casefold() not in content.casefold():
            FAILURES.append(f"{root.name}/{relative}: missing required marker {marker!r}")


def require_exact_checkout(root: Path, expected: object, label: str) -> None:
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{40}", expected):
        FAILURES.append(f"lock has an invalid immutable SHA for {label}")
        return
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode or result.stdout.strip() != expected:
        FAILURES.append(
            f"{label} checkout does not match lock: expected {expected}, "
            f"got {result.stdout.strip() or result.stderr.strip()}"
        )


def run_test_subset(root: Path, paths: tuple[str, ...], label: str) -> None:
    if not root.is_dir():
        FAILURES.append(f"{label} checkout is missing: {root}")
        return
    for path in paths:
        if not (root / path).is_file():
            FAILURES.append(f"{label} test file missing: {path}")
            return
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} tests failed:\n{result.stdout[-5000:]}\n{result.stderr[-2500:]}"
        )


def main() -> int:
    manifest = load_json(ROOT / "docs/ecosystem/ecosystem-manifest.json")
    lock = load_json(ROOT / "ecosystem.lock.json")
    repositories = lock.get("repositories", {})
    if not isinstance(repositories, dict):
        FAILURES.append("ecosystem lock repositories object is missing")
        repositories = {}
    if lock.get("baseline_id") != manifest.get("baseline_id"):
        FAILURES.append("P9 manifest and ecosystem lock baseline IDs differ")
    contracts = lock.get("contracts", {})
    if not isinstance(contracts, dict):
        FAILURES.append("P9 ecosystem lock contracts object is missing")
        contracts = {}
    if contracts.get("mcp_endpoint") != "POST /mcp":
        FAILURES.append("P9 lock does not pin the MCP HTTP entry point")
    if contracts.get("mcp_protocol_version") != "2026-07-28":
        FAILURES.append("P9 lock does not pin MCP protocol version 2026-07-28")
    if contracts.get("a2a_specification") != "1.0.1":
        FAILURES.append("P9 lock does not pin A2A specification 1.0.1")
    state = manifest.get("certification_state", {})
    if not isinstance(state, dict) or state.get("p9") not in {"in_progress", "certified"}:
        FAILURES.append("P9 certification state must be explicit")

    for key, root in (("platform", PLATFORM), ("os", OS), ("platform_sdk", SDK)):
        item = repositories.get(key, {})
        expected = item.get("ref") if isinstance(item, dict) else None
        require_exact_checkout(root, expected, key)

    authority = lock.get("integration_authority", {})
    expected_tsic = authority.get("ref") if isinstance(authority, dict) else None
    require_exact_checkout(TSIC, expected_tsic, "TSIC")

    baseline_path = TSIC / "policies/interoperability-baseline.json"
    tsic_baseline = load_json(baseline_path)
    if tsic_baseline.get("mcp_specification") != "2026-07-28":
        FAILURES.append("TSIC baseline does not pin MCP 2026-07-28")
    if tsic_baseline.get("a2a_specification") != "1.0.1":
        FAILURES.append("TSIC baseline does not pin A2A 1.0.1")

    require_file(
        PLATFORM,
        "packages/mcp/src/tinlance_agent_platform_mcp/protocol.py",
        "MCP_PROTOCOL_VERSION",
        "server/discover",
        "tools/list",
        "tools/call",
        "MCPPlatformRequest",
        "idempotency",
        "supportedVersions",
        "HeaderMismatch",
        "UnsupportedProtocolVersion",
        "-32020",
        "-32022",
        "resultType",
        "io.modelcontextprotocol/serverInfo",
    )
    require_file(
        PLATFORM,
        "packages/api/src/tinlance_agent_platform_api/http.py",
        'self.path == "/mcp"',
        "mcp_service",
        'self.path == "/a2a"',
        "a2a_service",
        "/.well-known/agent-card.json",
    )
    require_file(
        PLATFORM,
        "packages/api/src/tinlance_agent_platform_api/service.py",
        "request.tenant_id, request.subject_id, caller_key",
    )
    require_file(
        PLATFORM,
        "packages/multi_agent/src/tinlance_agent_platform_multi_agent/a2a_http.py",
        "A2AProtocolService",
        "message/send",
        "tasks/get",
        "application/a2a+json",
        "AgentCardSignatureVerifier",
        "card_verifier",
        "tenant_id",
        "subject_id",
        "idempotency-key",
    )
    require_file(
        PLATFORM,
        "packages/multi_agent/src/tinlance_agent_platform_multi_agent/interoperability.py",
        "A2A_SPECIFICATION_VERSION",
        "AgentCardSignatureVerifier",
        "RemoteCredentialProvider",
        "application/a2a+json",
        "validate_remote_endpoint",
        "expected_tenant_id",
        "expected_issuer_id",
        "expected_audience",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/interop.py",
        "supportedInterfaces",
        "unsupported MCP protocol version",
    )
    require_file(
        SDK,
        "src/tinlance_agent_platform_sdk/mcp.py",
        "_SUPPORTED_PROTOCOL_VERSIONS",
        "credential-shaped metadata",
    )
    require_file(
        TSIC,
        "scripts/certify_interoperability.py",
        "protocol_support_never_grants_execution_authority",
        "agent_card_signature_verification_required",
        "remote_credentials_must_be_scoped",
        "tenant_scoped_idempotency_required",
        "mcp_body_header_version_match_required",
        "application/a2a+json",
    )
    tsic_result = subprocess.run(
        [sys.executable, str(TSIC / "scripts/certify_interoperability.py")],
        cwd=TSIC,
        check=False,
        capture_output=True,
        text=True,
    )
    if tsic_result.returncode:
        FAILURES.append(
            f"TSIC interoperability certification failed:\n"
            f"{tsic_result.stdout[-3000:]}\n{tsic_result.stderr[-1500:]}"
        )

    run_test_subset(
        PLATFORM,
        (
            "tests/test_mcp_protocol.py",
            "tests/test_m17_interoperability.py",
            "tests/test_a2a_http.py",
            "tests/test_api_idempotency.py",
            "tests/test_a2a_http.py",
            "tests/test_api_idempotency.py",
        ),
        "Platform MCP/A2A protocol and adversarial boundary",
    )
    run_test_subset(OS, ("tests/unit/test_interop.py",), "Agent OS protocol metadata")
    run_test_subset(SDK, ("tests/test_m21_mcp_surface.py",), "Platform SDK MCP contracts")

    if FAILURES:
        print("P9 MCP/A2A interoperability conformance: FAIL")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("P9 MCP/A2A interoperability conformance: PASS")
    print(
        "Exact locked Platform, OS, SDK and TSIC revisions passed protocol and adversarial tests."
    )
    print(
        "Production network pinning, deployed authentication, shared rate limiting and telemetry "
        "remain deployment evidence requirements."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
