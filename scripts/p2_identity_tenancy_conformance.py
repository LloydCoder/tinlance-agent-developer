#!/usr/bin/env python3
"""Canonical P2 identity/tenancy conformance against exact locked revisions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
PLATFORM = Path("/tmp/tinlance-platform")
FAILURES: list[str] = []


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        FAILURES.append(f"cannot read {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        FAILURES.append(f"{path} must contain a JSON object")
        return {}
    return value


def require_markers(root: Path, relative: str, *markers: str) -> None:
    path = root / relative
    if not path.is_file():
        FAILURES.append(f"missing P2 evidence file: {path}")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker.lower() not in content.lower():
            FAILURES.append(f"{path}: missing P2 marker {marker!r}")


def verify_locked_revision(name: str, root: Path, lock: dict[str, object]) -> None:
    repositories = lock.get("repositories")
    if not isinstance(repositories, dict):
        FAILURES.append("ecosystem lock repositories map is invalid")
        return
    entry = repositories.get(name)
    if not isinstance(entry, dict):
        FAILURES.append(f"ecosystem lock missing repository {name!r}")
        return
    expected = entry.get("ref")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(f"cannot resolve {name} checkout HEAD: {result.stderr[-1000:]}")
        return
    actual = result.stdout.strip()
    if actual != expected:
        FAILURES.append(f"{name} checkout SHA {actual} does not match lock SHA {expected}")


def run_tests(root: Path, paths: tuple[str, ...], label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} failed:\\n{result.stdout[-5000:]}\\n{result.stderr[-2500:]}"
        )


def main() -> int:
    lock = read_json(ROOT / "ecosystem.lock.json")
    manifest = read_json(ROOT / "docs/ecosystem/ecosystem-manifest.json")
    state = manifest.get("certification_state", {})
    if not isinstance(state, dict):
        FAILURES.append("manifest certification state is invalid")
        state = {}
    if state.get("p0") != "certified" or state.get("p1") != "certified":
        FAILURES.append("P2 cannot start before canonical P0 and P1 are certified")
    p2_status = state.get("p2")
    if p2_status not in {"in_progress", "certified"}:
        FAILURES.append("manifest must mark canonical P2 in_progress or certified while this gate runs")
    active_phase = None
    if p2_status == "in_progress":
        expected_release = "p2_in_progress"
        active_phase = 2
    else:
        phase_statuses = [state.get(f"p{phase}") for phase in range(3, 11)]
        active_phases = [
            phase for phase, status in zip(range(3, 11), phase_statuses, strict=True)
            if status == "in_progress"
        ]
        if len(active_phases) > 1:
            FAILURES.append("only one canonical ecosystem phase may be in progress")
        if active_phases:
            active_phase = active_phases[0]
            expected_release = f"p{active_phase}_in_progress"
        elif all(status == "certified" for status in phase_statuses):
            expected_release = "all_phases_certified"
        else:
            first_not_started = next(
                (phase for phase, status in zip(range(3, 11), phase_statuses, strict=True)
                 if status != "certified"),
                10,
            )
            expected_release = f"ready_for_p{first_not_started}"
        for phase in range(3, 11):
            status = state.get(f"p{phase}")
            if active_phase is not None:
                expected_status = (
                    "certified" if phase < active_phase
                    else "in_progress" if phase == active_phase
                    else "not_started"
                )
            elif expected_release == "all_phases_certified":
                expected_status = "certified"
            else:
                ready_phase = int(expected_release.removeprefix("ready_for_p"))
                expected_status = "certified" if phase < ready_phase else "not_started"
            if status != expected_status:
                FAILURES.append(
                    f"P{phase} must be {expected_status} under the current serial release state"
                )
    if state.get("sequence_release") != expected_release:
        FAILURES.append(f"manifest sequence_release must be {expected_release}")
    if state.get("production") != "unverified":
        FAILURES.append("repository-only P2 tests cannot certify production deployment")

    for name, root in (
        ("platform", PLATFORM),
        ("os", OS),
        ("platform_sdk", SDK),
    ):
        verify_locked_revision(name, root, lock)

    require_markers(
        PLATFORM,
        "packages/identity/src/tinlance_agent_platform_identity/jwt_verifier.py",
        'expected_typ: str | None = "at+jwt"',
        "tenant claims are contradictory",
        "client_id",
    )
    require_markers(
        PLATFORM,
        "packages/identity/src/tinlance_agent_platform_identity/resolver.py",
        "class JWKSPrincipalResolver",
        "is_revoked",
        "PlatformAuthenticationFailure",
    )
    require_markers(
        PLATFORM,
        "packages/identity/src/tinlance_agent_platform_identity/revocation.py",
        "class TokenRevocationChecker",
        "PRIMARY KEY (issuer, token_id)",
    )
    require_markers(
        PLATFORM,
        "tests/test_identity_resolver.py",
        "test_revocation_backend_failure_fails_closed",
        "tenant-victim",
    )
    require_markers(
        OS,
        "tests/integration/test_platform_adapter_contract.py",
        "tenant_id",
        "subject_id",
    )
    require_markers(
        SDK,
        "tests/test_client.py",
        "tenant_id",
        "subject_id",
        "authorization",
    )

    run_tests(
        PLATFORM,
        (
            "tests/test_identity_jwt.py",
            "tests/test_identity_resolver.py",
            "tests/test_authorization_enforcement.py",
        ),
        "Platform identity and authorization",
    )
    run_tests(
        OS,
        (
            "tests/contract/test_platform_adapter.py",
            "tests/integration/test_platform_adapter_contract.py",
        ),
        "Agent OS identity-context transport",
    )
    run_tests(SDK, ("tests/test_client.py",), "Platform SDK tenant-context transport")

    if FAILURES:
        print("canonical P2 identity/tenancy conformance: FAIL")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    repositories = lock["repositories"]
    print(
        json.dumps(
            {
                "status": "pass",
                "phase": "P2",
                "scope": "identity-tenancy-authentication-authorization",
                "locked_revisions": {
                    name: repositories[name]["ref"]
                    for name in ("platform", "os", "platform_sdk")
                },
                "checks": [
                    "strict JWT/JWKS profile",
                    "tenant claim consistency",
                    "issuer+jti revocation and fail-closed outage",
                    "verified principal mapping",
                    "HTTP tenant/subject binding",
                    "OS tenant-context transport",
                    "SDK tenant-context transport",
                    "authorization regression",
                ],
                "production_status": "unverified",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
