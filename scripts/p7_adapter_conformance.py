"""Exact-SHA cross-repository gate for canonical ecosystem P7.

This gate validates the adapter boundary across Platform, OS, SDK and TSIC.
It does not claim live provider credentials or production deployment readiness.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "ecosystem.lock.json"
DEVELOPER = Path("/tmp/tinlance-developer")
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
PLATFORM = Path("/tmp/tinlance-platform")
TSIC = Path("/tmp/tinlance-tsic")

FAILURES: list[str] = []


def run_git_head(repository: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(f"cannot read pinned HEAD for {repository}: {result.stderr[-1000:]}")
        return ""
    return result.stdout.strip()


def require_pinned_repository(name: str, repository: Path, expected: str) -> None:
    actual = run_git_head(repository)
    if actual != expected:
        FAILURES.append(f"{name} SHA mismatch: lock={expected}, checkout={actual}")


def require_file_markers(repository: Path, relative: str, markers: tuple[str, ...]) -> None:
    path = repository / relative
    if not path.is_file():
        FAILURES.append(f"missing P7 adapter artifact: {path}")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker not in content:
            FAILURES.append(f"{path}: missing required marker {marker!r}")


def run_test_subset(repository: Path, paths: tuple[str, ...], label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} conformance tests failed:\n"
            f"{result.stdout[-5000:]}\n{result.stderr[-2500:]}"
        )


def main() -> int:
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        repositories = lock["repositories"]
        authority = lock["integration_authority"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"P7 lock could not be loaded: {exc}", file=sys.stderr)
        return 2

    paths = {
        "developer": DEVELOPER,
        "os": OS,
        "platform": PLATFORM,
        "platform_sdk": SDK,
    }
    for name, repository in paths.items():
        item = repositories.get(name, {})
        require_pinned_repository(name, repository, str(item.get("ref", "")))
    require_pinned_repository("tsic", TSIC, str(authority.get("ref", "")))

    require_file_markers(
        PLATFORM,
        "packages/models/src/tinlance_agent_platform_models/openai_compatible.py",
        (
            "credential_provider.token(request)",
            "provider redirects are disabled",
            "max_response_bytes",
            'headers["traceparent"]',
        ),
    )
    require_file_markers(
        PLATFORM,
        "packages/secrets/src/tinlance_agent_platform_secrets/model_provider.py",
        ("class ScopedModelCredentialProvider", "resolve_for_execution", "capability_id"),
    )
    require_file_markers(
        OS,
        "src/tinlance_agent_os/transport.py",
        ("_TRACEPARENT", 'headers["traceparent"] = context.traceparent'),
    )
    require_file_markers(
        SDK,
        "src/tinlance_agent_platform_sdk/client.py",
        ("def _validate_traceparent", 'raise ValueError("traceparent version must be 00")'),
    )
    require_file_markers(
        TSIC,
        "contracts/models/provider-adapter-boundary.json",
        ("provider-adapter-boundary", "W3C Trace Context"),
    )

    run_test_subset(
        PLATFORM,
        ("tests/unit/test_openai_compatible_provider.py", "tests/architecture/test_boundaries.py"),
        "Platform",
    )
    run_test_subset(OS, ("tests/unit/test_transport.py",), "Agent OS")
    run_test_subset(SDK, ("tests/test_client.py",), "Platform SDK")
    run_test_subset(TSIC, ("tests/test_provider_adapter_boundary.py",), "TSIC")

    if FAILURES:
        print("Canonical P7 adapter conformance FAILED:")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("Canonical P7 adapter conformance PASSED for exact locked SHAs.")
    print("This is repository-level evidence only; live providers and production infrastructure remain unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
