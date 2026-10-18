"""Canonical ecosystem P10 end-to-end recovery conformance gate.

This gate must run only against exact reviewed SHAs materialized from
ecosystem.lock.json. It combines recovery-objective, durable-event/replay and
bounded-retry regressions across Platform, OS and SDK with replica invariants.
It does not assert external production readiness.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVELOPER = Path("/tmp/tinlance-developer")
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
PLATFORM = Path("/tmp/tinlance-platform")
TSIC = Path("/tmp/tinlance-tsic")
FAILURES: list[str] = []


def fail(message: str) -> None:
    FAILURES.append(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
        return {}
    return value


def check_pin(name: str, repository: Path, expected: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        fail(f"cannot read {name} checkout SHA: {result.stderr[-1000:]}")
    elif not re.fullmatch(r"[0-9a-f]{40}", expected) or result.stdout.strip() != expected:
        fail(f"{name} checkout SHA differs from the reviewed lock")


def run_tests(repository: Path, paths: tuple[str, ...], label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
        timeout=240,
    )
    if result.returncode:
        fail(
            f"{label} recovery tests failed (exit {result.returncode}):\n"
            f"{result.stdout[-3500:]}\n{result.stderr[-2500:]}"
        )


def main() -> int:
    lock = read_json(ROOT / "ecosystem.lock.json")
    manifest = read_json(ROOT / "docs/ecosystem/ecosystem-manifest.json")
    replicas = read_json(ROOT / "docs/ecosystem/replication-manifest.json")
    repos = lock.get("repositories", {})
    authority = lock.get("integration_authority", {})
    roots = {
        "developer": DEVELOPER,
        "os": OS,
        "platform_sdk": SDK,
        "platform": PLATFORM,
    }
    if set(repos) != {"developer", "os", "platform_sdk", "platform"}:
        fail("P10 requires exactly the four canonical repositories")
    for name, root in roots.items():
        entry = repos.get(name, {})
        check_pin(name, root, str(entry.get("ref", "")))
        if manifest.get("repositories"):
            item = next((r for r in manifest["repositories"] if r.get("id") == name), {})
            if item.get("reviewed_sha") != entry.get("ref"):
                fail(f"manifest and lock disagree on {name} SHA")
    check_pin("TSIC", TSIC, str(authority.get("ref", "")))
    tsic_contract = read_json(TSIC / "contracts/recovery/ecosystem-p10-recovery.json")
    if tsic_contract.get("canonical_ecosystem_phase") != "P10":
        fail("TSIC canonical ecosystem P10 recovery contract is missing or mismatched")
    if tsic_contract.get("authority_plane") != "LloydCoder/tinlance-agent-platform":
        fail("TSIC P10 contract does not preserve Platform as sole authority")

    if manifest.get("certification_state", {}).get("p10") not in ("in_progress", "certified"):
        fail("P10 must be explicitly in progress or certified")
    if manifest.get("certification_state", {}).get("production") != "unverified":
        fail("repository conformance must not silently assert external production readiness")
    if replicas.get("schema") != "replication/v1" or replicas.get("authority_plane") != "platform":
        fail("replication fixture must retain the canonical schema and Platform authority")
    entries = replicas.get("replicas", [])
    if len(entries) != 2:
        fail("P10 requires two independent tenant replicas")
    for field in ("id", "tenant_id", "workspace_id"):
        values = [entry.get(field) for entry in entries]
        if not all(isinstance(value, str) and value.strip() for value in values):
            fail(f"replicas require non-empty {field}")
        if len(set(values)) != len(values):
            fail(f"replica {field} values must be unique")

    run_tests(
        PLATFORM,
        ("tests/test_recovery_gate.py", "tests/test_m15_durability.py"),
        "Platform",
    )
    run_tests(OS, ("tests/test_event_runtime.py",), "Agent OS")
    run_tests(SDK, ("tests/test_retry.py",), "Platform SDK")
    run_tests(TSIC, ("tests/test_ecosystem_p10_recovery_contract.py",), "TSIC")

    if FAILURES:
        print("Canonical P10 recovery conformance FAILED:")
        for item in FAILURES:
            print(f"- {item}")
        return 1
    print("PASS canonical P10 repository recovery conformance for exact locked SHAs.")
    print(
        "External deployment, live backup/restore, TLS/OAuth/JWKS and "
        "production telemetry remain unverified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
