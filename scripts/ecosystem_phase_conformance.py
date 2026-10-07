"""Full ecosystem phase certification for the Tinlance Agent System.

This gate complements repository-local CI. It verifies that the exact locked
four-repository baseline still contains executable/documented evidence for
every finite ecosystem phase P0-P10, including the final replication boundary.

It deliberately distinguishes repository evidence from external production
infrastructure and never treats descriptive metadata as authority.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
OS = Path("/tmp/tinlance-os")
SDK = Path("/tmp/tinlance-platform_sdk")
PLATFORM = Path("/tmp/tinlance-platform")

FAILURES: list[str] = []


def require_file(root: Path, relative: str, *markers: str) -> None:
    path = root / relative
    if not path.is_file():
        FAILURES.append(f"missing file: {root.name}/{relative}")
        return
    content = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker.lower() not in content.lower():
            FAILURES.append(f"{root.name}/{relative}: missing marker {marker!r}")


def require_files(root: Path, files: tuple[str, ...]) -> None:
    for relative in files:
        require_file(root, relative)


def run_test_subset(cwd: Path, paths: tuple[str, ...], label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} tests failed:\n{result.stdout[-4000:]}\n{result.stderr[-2000:]}"
        )


def load_json(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        FAILURES.append(f"invalid JSON {relative}: {exc}")
        return {}
    if not isinstance(value, dict):
        FAILURES.append(f"JSON root must be an object: {relative}")
        return {}
    return value


def run_node_test_subset(cwd: Path, paths: tuple[str, ...], label: str) -> None:
    result = subprocess.run(
        ["node", "--test", *paths],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            f"{label} tests failed:\\n{result.stdout[-4000:]}\\n{result.stderr[-2000:]}"
        )


def phase_p1_transformation() -> None:
    require_file(ROOT, "docs/ecosystem/P1-TRANSFORMATION.md", "transformation/v1")
    require_file(ROOT, "docs/ecosystem/ecosystem-manifest.json", "transformation/v1")
    require_file(ROOT, "schemas/transformation/v1/transformation.schema.json", "outcome")
    require_file(ROOT, "schemas/examples/transformation.v1.json", "outcome")
    require_file(OS, "src/tinlance_agent_os/transformation.py", "Transformation")
    require_file(SDK, "src/tinlance_agent_platform_sdk/transformation.py", "Transformation")
    require_file(
        PLATFORM,
        "packages/contracts/src/tinlance_agent_platform_contracts/transformation.py",
        "Transformation",
    )
    run_node_test_subset(ROOT, ("tests/contract/schema-contracts.test.mjs",), "P1 TADL")
    run_test_subset(OS, ("tests/test_transformation.py",), "P1 Agent OS")
    run_test_subset(SDK, ("tests/test_transformation.py",), "P1 SDK")
    run_test_subset(PLATFORM, ("tests/contracts/test_transformation.py",), "P1 Platform")


def phase_p4_catalog() -> None:
    require_file(
        OS,
        "docs/P4-20K-CANONICAL-MILESTONE.md",
        "20K",
        "semantic uniqueness",
        "provenance",
        "review evidence",
        "continuous taxonomy",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_expansion_20k.py",
        "TARGET_COUNT = 20_000",
        "MIN_DOMAINS = 50",
        "semantic uniqueness",
    )
    require_file(OS, "tests/unit/test_catalog_expansion_20k.py", "20_000", "20K")
    require_file(OS, "tests/unit/test_catalog_20k_ga_semantics.py", "not a hard ceiling")
    # The fixture proves the release gate at scale; it is intentionally not
    # presented as 20,000 real-world reviewed archetypes.
    run_test_subset(
        OS,
        (
            "tests/unit/test_catalog_expansion_20k.py",
            "tests/unit/test_catalog_20k_ga_semantics.py",
            "tests/unit/test_catalog_governance.py",
        ),
        "P4 catalog",
    )


def phase_p6_runtime() -> None:
    require_file(
        PLATFORM,
        "docs/production-runtime/P6-PRODUCTION-RUNTIME-CONTRACT.md",
        "PostgreSQL",
        "durable",
        "backup",
        "restore",
    )
    require_files(
        PLATFORM,
        (
            "tests/test_p6_production_runtime_contract.py",
            "tests/test_m15_durability.py",
            "tests/test_m18_reliability.py",
            "tests/test_m21_production_infrastructure.py",
            "tests/test_m25_reliability_dr.py",
        ),
    )
    run_test_subset(
        PLATFORM,
        (
            "tests/test_m15_durability.py",
            "tests/test_m18_reliability.py",
            "tests/test_m21_production_infrastructure.py",
            "tests/test_m25_reliability_dr.py",
        ),
        "P6 runtime",
    )


def phase_p7_evaluation() -> None:
    require_file(
        PLATFORM,
        "docs/P7-EVALUATION-SAFETY.md",
        "adversarial",
        "safety-critical",
        "cannot create",
        "authority",
    )
    require_files(
        PLATFORM,
        (
            "tests/test_p7_evaluation_safety.py",
            "tests/test_m24_adversarial_security.py",
        ),
    )
    run_test_subset(
        PLATFORM,
        ("tests/test_p7_evaluation_safety.py", "tests/test_m24_adversarial_security.py"),
        "P7 evaluation",
    )


def phase_p8_control_plane() -> None:
    require_file(
        PLATFORM,
        "docs/P8-ENTERPRISE-CONTROL-PLANE.md",
        "organization",
        "tenancy",
        "approval",
        "budget",
        "sole authority",
    )
    require_files(
        PLATFORM,
        (
            "tests/test_m20_control_expansion.py",
            "tests/test_m23_registry_governance.py",
            "tests/test_m27_sre_compliance.py",
        ),
    )
    run_test_subset(
        PLATFORM,
        (
            "tests/test_m20_control_expansion.py",
            "tests/test_m23_registry_governance.py",
            "tests/test_m27_sre_compliance.py",
        ),
        "P8 control plane",
    )


def phase_p9_reference_enterprise() -> None:
    require_file(
        PLATFORM,
        "reference_agents/docs/WORKFORCE.md",
        "eleven governed roles",
        "authority-free",
        "Platform identity",
    )
    require_file(
        PLATFORM,
        "reference_agents/src/tinlance_reference_agents/workforce.py",
        "REFERENCE_WORKFORCE",
        "Executive",
        "Compliance",
    )
    run_test_subset(
        PLATFORM,
        (
            "reference_agents/tests/test_workforce.py",
            "reference_agents/tests/test_agents.py",
            "reference_agents/tests/test_contract_boundary.py",
        ),
        "P9 reference workforce",
    )


def phase_p10_replication() -> None:
    manifest = load_json(ROOT, "docs/ecosystem/ecosystem-manifest.json")
    replication = load_json(ROOT, "docs/ecosystem/replication-manifest.json")
    if manifest.get("phase") != "P10":
        FAILURES.append("P10 manifest phase is not P10")
    if manifest.get("baseline_id") != "p10-2026-10-07":
        FAILURES.append("P10 baseline ID drifted")
    if replication.get("schema") != "replication/v1":
        FAILURES.append("replication manifest schema drifted")
    if replication.get("authority_plane") != "platform":
        FAILURES.append("replication authority plane drifted")
    replicas = replication.get("replicas")
    if not isinstance(replicas, list) or len(replicas) != 2:
        FAILURES.append("P10 requires exactly two deterministic replicas")
        return
    tenant_ids = {item.get("tenant_id") for item in replicas if isinstance(item, dict)}
    workspace_ids = {item.get("workspace_id") for item in replicas if isinstance(item, dict)}
    if len(tenant_ids) != 2 or None in tenant_ids:
        FAILURES.append("P10 replica tenant IDs are not unique and complete")
    if len(workspace_ids) != 2 or None in workspace_ids:
        FAILURES.append("P10 replica workspace IDs are not unique and complete")
    for item in replicas:
        if not isinstance(item, dict) or not item.get("id"):
            FAILURES.append("P10 replica IDs must be stable and non-empty")

    require_file(
        ROOT,
        "docs/ecosystem/P10-REPLICATION-GA.md",
        "parameterized",
        "cross-tenant",
        "Platform remains the sole",
        "does not claim",
    )
    require_file(ROOT, "scripts/validate-ecosystem-manifest.mjs", "replication/v1")
    run_node_test_subset(ROOT, ("tests/contract/architecture-boundaries.test.mjs",), "P10 TADL")


def main() -> int:
    # P0 is the enclosing manifest/lock gate; P2/P3/P5 have dedicated
    # certification scripts in the existing workflow. This script closes the
    # previously missing P1/P4/P6/P7/P8/P9/P10 coverage.
    phase_p1_transformation()
    phase_p4_catalog()
    phase_p6_runtime()
    phase_p7_evaluation()
    phase_p8_control_plane()
    phase_p9_reference_enterprise()
    phase_p10_replication()

    if FAILURES:
        print("full ecosystem phase certification: FAIL")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("full ecosystem phase certification: PASS")
    print("P1/P4/P6/P7/P8/P9/P10 are green against the locked four-repository baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
