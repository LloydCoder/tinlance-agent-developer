"""Canonical P8 cross-repository budget/quota/capacity conformance.

Platform owns quota admission, settlement, recovery and cost evidence. OS and
SDK must consume Platform-governed results without introducing a second ledger
or local authorization path. This gate validates the exact refs in ecosystem.lock.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = Path("/tmp/tinlance-platform")
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
FAILURES: list[str] = []


def require_markers(path: Path, *markers: str) -> str:
    if not path.is_file():
        FAILURES.append(f"missing P8 implementation file: {path}")
        return ""
    content = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker.lower() not in content.lower():
            FAILURES.append(f"{path.relative_to(PLATFORM)}: missing marker {marker!r}")
    return content


def locked_sha(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(f"cannot resolve exact locked SHA for {repo}: {result.stderr[-1000:]}")
        return ""
    return result.stdout.strip()


def check_authority_boundary() -> None:
    migration = require_markers(
        PLATFORM / "database/migrations/010_p8_budget_quota_ledger.sql",
        "platform.tenant_budget_limits",
        "platform.organization_budget_limits",
        "platform.quota_reservations",
        "platform.quota_ledger",
        "FOR UPDATE",
        "platform.reserve_quota",
        "platform.settle_quota",
        "platform.release_quota",
        "ENABLE ROW LEVEL SECURITY",
        "FORCE ROW LEVEL SECURITY",
        "quota_ledger_append_only",
        "quota_ledger_no_truncate",
        "quota_evidence_is_safe",
        "measurement_ref",
        "prior_settlement.evidence = coalesce(p_evidence, '{}'::jsonb)",
    )
    recovery = require_markers(
        PLATFORM / "database/migrations/011_p8_quota_reservation_recovery.sql",
        "lease_expires_at",
        "request_expired_quota_reconciliation",
        "FOR UPDATE SKIP LOCKED",
        "recovery_requested",
        "confirmed-no-side-effect",
        "expired reservation must enter reconciliation before release",
        "recovery_evidence_ref",
        "recovery_resolved_at",
    )
    require_markers(
        PLATFORM / "database/tests/006_p8_quota_ledger.sql",
        "settlement replay accepted conflicting evidence",
        "append-only ledger allowed an update",
        "append-only ledger allowed truncation",
    )
    require_markers(
        PLATFORM / "database/tests/007_p8_quota_concurrency.sql",
        "create extension if not exists dblink",
        "concurrent",
        "concurrent admission oversubscribed tenant concurrency",
        "organization quota",
    )
    require_markers(
        PLATFORM / "database/tests/008_p8_quota_recovery.sql",
        "expired reservation was released before reconciliation",
        "recovery-requested reservation was released",
        "confirmed-no-side-effect",
        "reconciliation could not settle measured usage",
    )
    require_markers(
        PLATFORM / "tests/test_p8_budget_quota_ledger.py",
        "PostgresQuotaLedger",
        "test_postgres_ledger_exposes_lease_renewal_and_reconciliation",
        "test_p8_migration_has_transactional_limits_rls_and_append_only_ledger",
    )
    if "security invoker" not in migration.lower() or "security invoker" not in recovery.lower():
        FAILURES.append("P8 SQL functions must preserve caller identity and RLS via SECURITY INVOKER")


def check_consumer_boundary() -> None:
    for repo, label in ((OS, "Agent OS"), (SDK, "Platform SDK")):
        source = repo / "src"
        if not source.is_dir():
            FAILURES.append(f"{label} source directory is missing")
            continue
        for path in source.rglob("*.py"):
            content = path.read_text(encoding="utf-8", errors="replace").lower()
            forbidden = (
                "platform.quota_ledger",
                "platform.quota_reservations",
                "platform.reserve_quota(",
                "platform.settle_quota(",
                "platform.release_quota(",
            )
            for marker in forbidden:
                if marker in content:
                    FAILURES.append(
                        f"{label} duplicates Platform-owned quota persistence: "
                        f"{path.relative_to(repo)} contains {marker!r}"
                    )


def check_exact_lock() -> None:
    lock = json.loads((ROOT / "ecosystem.lock.json").read_text(encoding="utf-8"))
    expected = {
        "platform": (PLATFORM, lock["repositories"]["platform"]["ref"]),
        "os": (OS, lock["repositories"]["os"]["ref"]),
        "platform_sdk": (SDK, lock["repositories"]["platform_sdk"]["ref"]),
    }
    for name, (repo, expected_sha) in expected.items():
        actual = locked_sha(repo)
        if actual != expected_sha:
            FAILURES.append(
                f"ecosystem lock drift for {name}: expected {expected_sha}, got {actual}"
            )


def run_platform_p8_tests() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_p8_budget_quota_ledger.py"],
        cwd=PLATFORM,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            "Platform P8 unit/adapter tests failed against the locked SHA:\\n"
            + result.stdout[-5000:]
            + "\\n"
            + result.stderr[-2500:]
        )


def main() -> int:
    check_exact_lock()
    check_authority_boundary()
    check_consumer_boundary()
    run_platform_p8_tests()
    if FAILURES:
        print("P8 quota/budget conformance FAILED")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("P8 quota/budget conformance PASSED against exact locked repository SHAs")
    print("Platform owns admission, settlement, recovery, and ledger authority.")
    print("Agent OS and SDK do not duplicate quota persistence or execution authority.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
