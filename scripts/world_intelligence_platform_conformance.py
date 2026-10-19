#!/usr/bin/env python3
"""Fail the ecosystem gate when any mandatory TSIC query requirement lacks collected tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TSIC_ROOT = Path(os.environ.get("TSIC_ROOT", "/tmp/tinlance-tsic"))
PLATFORM_ROOT = Path(os.environ.get("PLATFORM_ROOT", "/tmp/tinlance-platform"))
REQUIREMENTS_RELATIVE = Path("conformance/requirements/world-intelligence-platform-query.json")
MAP_PATH = ROOT / "docs/ecosystem/world-intelligence-platform-query-test-map.json"


def fail(message: str) -> int:
    print(f"World Intelligence Platform conformance: {message}", file=sys.stderr)
    return 1


def main() -> int:
    requirements_path = TSIC_ROOT / REQUIREMENTS_RELATIVE
    if not requirements_path.is_file():
        return fail(f"missing pinned TSIC requirements file: {requirements_path}")
    if not MAP_PATH.is_file():
        return fail(f"missing test map: {MAP_PATH}")

    try:
        contract = json.loads(requirements_path.read_text(encoding="utf-8"))
        test_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"invalid JSON contract or test map: {exc}")

    if contract.get("status") != "required":
        return fail("TSIC query contract is not marked required")
    if test_map.get("contract_id") != contract.get("id"):
        return fail("test map does not reference the exact TSIC contract ID")
    requirement_rows = contract.get("requirements", [])
    requirement_ids = [
        item.get("id")
        for item in requirement_rows
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if len(requirement_ids) != len(set(requirement_ids)):
        return fail("TSIC contract contains duplicate requirement IDs")
    mandatory = {
        item.get("id")
        for item in requirement_rows
        if isinstance(item, dict)
        and item.get("mandatory") is True
        and isinstance(item.get("id"), str)
    }
    mapped_entries = test_map.get("requirements", [])
    if not isinstance(mapped_entries, list) or any(
        not isinstance(item, dict) for item in mapped_entries
    ):
        return fail("test map requirements must be a list of objects")
    mapped_ids = {
        item.get("id")
        for item in mapped_entries
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if not mandatory:
        return fail("TSIC query contract has no mandatory requirements")
    if mandatory != mapped_ids:
        missing = sorted(mandatory - mapped_ids)
        extra = sorted(mapped_ids - mandatory)
        return fail(f"test-map mismatch; missing={missing}, extra={extra}")

    mapped_tests: set[str] = set()
    for item in mapped_entries:
        tests = item.get("tests")
        if not isinstance(tests, list) or not tests or any(
            not isinstance(name, str) or not name for name in tests
        ):
            return fail(f"{item.get('id')} has no valid executable test mapping")
        mapped_tests.update(tests)

    platform_tests = PLATFORM_ROOT / "tests/test_world_intelligence_mcp_integration.py"
    e2e_test = ROOT / "tests/integration/test_platform_world_intelligence_query_e2e.py"
    for path in (platform_tests, e2e_test):
        if not path.is_file():
            return fail(f"missing test source: {path}")

    command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        str(platform_tests),
        str(e2e_test),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        print(output, file=sys.stderr)
        return fail("pytest collection failed")

    missing_tests = sorted(name for name in mapped_tests if name not in output)
    if missing_tests:
        return fail(f"mapped tests were not collected: {missing_tests}")

    print(
        "World Intelligence Platform conformance: "
        f"{len(mandatory)} mandatory requirements mapped to "
        f"{len(mapped_tests)} collected tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
