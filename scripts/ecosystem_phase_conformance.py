"""Cross-cutting component regression gate for the Tinlance Agent System.

This script runs the P1 Transformation contract checks and supporting
catalog/runtime/evaluation/control-plane/workforce/replication component suites
against exact locked repository revisions. These component suites are not, by
themselves, certification of a similarly numbered canonical ecosystem phase.
The canonical sequence and its current state are defined by PHASE-MATRIX.md and
ecosystem-manifest.json. External production infrastructure remains unverified.
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


def validate_real_sdk_transformation_payload() -> None:
    """Validate a serialized SDK model against the canonical TADL schema."""
    sdk_source = str(SDK / "src")
    if sdk_source not in sys.path:
        sys.path.insert(0, sdk_source)
    try:
        from tinlance_agent_platform_sdk import (
            Transformation,
            TransformationOutcome,
            TransformationProvenance,
            TransformationReference,
        )
    except ImportError as exc:
        FAILURES.append(f"cannot import locked SDK Transformation model: {exc}")
        return
    from uuid import UUID

    try:
        item = Transformation(
            transformation_id=UUID("2f6d7a8a-5a12-4f8b-9a3e-3c1c2f4d8e11"),
            tenant_ref="tenant:conformance",
            version=1,
            objective="Validate canonical transformation contract",
            success_criteria=("Produce a schema-valid payload",),
            principal_ref="principal:conformance",
            agent_ref="agent:conformance",
            agent_version="1.0.0",
            workspace_ref="workspace:conformance",
            task_ref="task:conformance",
            requested_capabilities=(("capability:conformance.read", "validate contract"),),
            policy_refs=("policy:conformance",),
            risk_class="low",
            idempotency_key="transformation-conformance-v1",
            execution_state="succeeded",
            run_ref="run:conformance",
            output_refs=(TransformationReference("artifact:result", "result"),),
            evidence_refs=(TransformationReference("evidence:result", "execution"),),
            outcome=TransformationOutcome("achieved", True),
            provenance=TransformationProvenance(
                declared_by="tadl:p1",
                recorded_at="2026-10-17T18:00:00Z",
            ),
        )
        payload = item.as_payload()
    except Exception as exc:
        FAILURES.append(f"SDK Transformation fixture failed: {type(exc).__name__}: {exc}")
        return
    validator = (
        'import { validateArtifact } from "./packages/schemas/src/index.mjs";'
        'let raw = ""; for await (const chunk of process.stdin) raw += chunk;'
        'const result = validateArtifact("transformation/v1/transformation.schema.json", JSON.parse(raw));'
        'if (!result.valid) { console.error(JSON.stringify(result.errors)); process.exit(1); }'
    )
    result = subprocess.run(
        ["node", "--input-type=module", "-e", validator],
        cwd=ROOT,
        input=json.dumps(payload),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        FAILURES.append(
            "serialized SDK Transformation payload violates canonical schema: "
            + result.stderr[-2500:]
            + result.stdout[-1500:]
        )


def phase_p1_transformation() -> None:
    require_file(ROOT, "docs/ecosystem/P1-TRANSFORMATION.md", "transformation/v1")
    require_file(ROOT, "docs/ecosystem/ecosystem-manifest.json", "transformation/v1")
    require_file(ROOT, "schemas/transformation/v1/transformation.schema.json", "outcome")
    require_file(ROOT, "schemas/examples/transformation.v1.json", "outcome")
    require_file(OS, "src/tinlance_agent_os/transformation.py", "Transformation")
    require_file(SDK, "src/tinlance_agent_platform_sdk/transformation.py", "Transformation")
    sdk_transformation = SDK / "src/tinlance_agent_platform_sdk/transformation.py"
    if sdk_transformation.is_file():
        sdk_source = sdk_transformation.read_text(encoding="utf-8", errors="replace")
        for marker in ('"provenance"', '"declared_by"', '"recorded_at"'):
            if marker not in sdk_source:
                FAILURES.append(
                    f"SDK Transformation serializer is missing canonical provenance marker {marker}"
                )
        if '"constraints": {}' in sdk_source:
            FAILURES.append("SDK Transformation serializer drops caller-supplied constraints")
        if 'if self.achieved and self.status != "achieved"' not in sdk_source:
            FAILURES.append("SDK Transformation outcome permits achieved=true with a non-achieved status")
    require_file(
        PLATFORM,
        "packages/contracts/src/tinlance_agent_platform_contracts/transformation.py",
        "Transformation",
    )
    run_node_test_subset(ROOT, ("tests/contract/schema-contracts.test.mjs",), "P1 TADL")
    run_test_subset(OS, ("tests/test_transformation.py",), "P1 Agent OS")
    run_test_subset(SDK, ("tests/test_transformation.py",), "P1 SDK")
    run_test_subset(PLATFORM, ("tests/contracts/test_transformation.py",), "P1 Platform")
    validate_real_sdk_transformation_payload()


def check_catalog_release_gate() -> None:
    require_file(
        OS,
        "docs/P4-20K-CANONICAL-MILESTONE.md",
        "20K",
        "semantic uniqueness",
        "provenance",
        "review evidence",
        "continuous taxonomy",
        "Synthetic test fixtures",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_semantics.py",
        "canonical_semantic_key",
        "normalize_semantic_token",
        "NFKC",
        "casefold",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_expansion_20k.py",
        "TARGET_COUNT = 20_000",
        "MIN_DOMAINS = 50",
        "canonical_semantic_key",
        "semantic uniqueness",
        "inventory_digest",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_release.py",
        "10K",
        "canonical_semantic_key",
        "review evidence for every entry",
        "inventory_digest",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_forensics.py",
        "audit_canonical_inventory",
        "semantic archetype duplicates",
        "audit_digest",
    )
    require_file(
        OS,
        "src/tinlance_agent_os/catalog_governance.py",
        "prepare_evolution_release",
        "semantic duplicates",
        "deprecated",
        "governance evidence",
    )
    require_files(
        OS,
        (
            "tests/unit/test_catalog_expansion_20k.py",
            "tests/unit/test_catalog_20k_ga_semantics.py",
            "tests/unit/test_catalog_governance.py",
            "tests/unit/test_catalog_forensics.py",
            "tests/unit/test_catalog_release.py",
            "tests/unit/test_catalog_candidates.py",
            "tests/unit/test_catalog_semantic_identity.py",
            "tests/unit/test_catalog_taxonomy.py",
            "tests/unit/test_catalog_pipeline.py",
        ),
    )
    # Synthetic fixtures prove the fail-closed release gate at scale; they are
    # not represented as 20,000 real-world reviewed archetypes.
    run_test_subset(
        OS,
        (
            "tests/unit/test_catalog_expansion_20k.py",
            "tests/unit/test_catalog_20k_ga_semantics.py",
            "tests/unit/test_catalog_governance.py",
            "tests/unit/test_catalog_forensics.py",
            "tests/unit/test_catalog_release.py",
            "tests/unit/test_catalog_candidates.py",
            "tests/unit/test_catalog_semantic_identity.py",
            "tests/unit/test_catalog_taxonomy.py",
            "tests/unit/test_catalog_pipeline.py",
        ),
        "cross-cutting catalog release gate",
    )


def check_production_runtime_contract() -> None:
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
            "tests/test_p6_production_runtime_contract.py",
            "tests/test_m15_durability.py",
            "tests/test_m18_reliability.py",
            "tests/test_m21_production_infrastructure.py",
            "tests/test_m25_reliability_dr.py",
        ),
        "cross-cutting production-runtime contract",
    )


def check_evaluation_safety_gate() -> None:
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
        "cross-cutting evaluation-safety gate",
    )


def check_enterprise_control_plane() -> None:
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
        "cross-cutting enterprise-control-plane gate",
    )


def check_reference_enterprise_workforce() -> None:
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
        "cross-cutting reference-enterprise workforce",
    )


def check_replication_contract_integrity() -> None:
    manifest = load_json(ROOT, "docs/ecosystem/ecosystem-manifest.json")
    replication = load_json(ROOT, "docs/ecosystem/replication-manifest.json")
    lock = load_json(ROOT, "ecosystem.lock.json")
    if manifest.get("phase") != "P10":
        FAILURES.append("manifest contract-surface marker must remain P10 for replication artifact validation")
    locked_baseline = lock.get("baseline_id")
    if not isinstance(locked_baseline, str) or not locked_baseline:
        FAILURES.append("ecosystem lock does not declare a baseline ID")
    elif manifest.get("baseline_id") != locked_baseline:
        FAILURES.append("replication contract baseline ID does not match the reviewed ecosystem lock")
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
    sdk_lock = str(load_json(ROOT, "ecosystem.lock.json").get("repositories", {}).get("platform_sdk", {}).get("ref", ""))
    reference_agents = PLATFORM / "reference_agents/pyproject.toml"
    if reference_agents.is_file():
        reference_text = reference_agents.read_text(encoding="utf-8")
        if sdk_lock not in reference_text:
            FAILURES.append("P10 reference agents do not pin the locked SDK revision")
    else:
        FAILURES.append("P10 reference-agent package metadata is missing")
    if (PLATFORM / "packages/sdk/src/tinlance_agent_platform_sdk").exists():
        FAILURES.append("P10 Platform ships a colliding tinlance_agent_platform_sdk namespace")
    if not (PLATFORM / "packages/sdk/src/tinlance_agent_platform_domain_sdk").exists():
        FAILURES.append("P10 Platform internal SDK namespace is missing")
    run_node_test_subset(ROOT, ("tests/contract/architecture-boundaries.test.mjs",), "P10 TADL")


def validate_canonical_phase_map() -> None:
    matrix = ROOT / "docs/ecosystem/PHASE-MATRIX.md"
    if not matrix.is_file():
        FAILURES.append("canonical phase matrix is missing")
        return
    content = matrix.read_text(encoding="utf-8", errors="replace").lower()
    expected = {
        "p0": "forensic baseline and reconciliation",
        "p1": "canonical contracts",
        "p2": "identity, tenancy",
        "p3": "event delivery",
        "p4": "trace context and evidence lineage",
        "p5": "registries and lifecycle governance",
        "p6": "model/tool routing and mediation",
        "p7": "real adapters and integration boundaries",
        "p8": "budgets, quotas, capacity and cost enforcement",
        "p9": "mcp/a2a interoperability and security",
        "p10": "end-to-end recovery and production certification",
    }
    for phase, scope in expected.items():
        if scope not in content:
            FAILURES.append(f"canonical phase map {phase} scope mismatch; expected {scope!r}")
    manifest = load_json(ROOT, "docs/ecosystem/ecosystem-manifest.json")
    state = manifest.get("certification_state", {})
    if not isinstance(state, dict):
        FAILURES.append("canonical certification state is missing")
        return
    if state.get("sequence_release") not in {
        "ready_for_p2", "p2_in_progress", "ready_for_p3", "p3_in_progress",
        "ready_for_p4", "p4_in_progress", "ready_for_p5", "p5_in_progress",
        "ready_for_p6", "p6_in_progress", "ready_for_p7", "p7_in_progress",
        "ready_for_p8", "p8_in_progress", "ready_for_p9", "p9_in_progress",
        "ready_for_p10", "p10_in_progress", "p10_complete", "all_phases_certified",
    }:
        FAILURES.append("canonical sequence release state is invalid or still uses the legacy phase map")


def main() -> int:
    # This is a supporting component regression gate, not a substitute for
    # the serial canonical phase-specific exit gate.
    validate_canonical_phase_map()
    phase_p1_transformation()
    check_catalog_release_gate()
    check_production_runtime_contract()
    check_evaluation_safety_gate()
    check_enterprise_control_plane()
    check_reference_enterprise_workforce()
    check_replication_contract_integrity()

    if FAILURES:
        print("ecosystem component regression gate: FAIL")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("ecosystem component regression gate: PASS")
    print("P1 Transformation and supporting component regression suites passed against the locked baseline.")
    print("Canonical P2-P10 completion still requires its own phase-specific gates and post-phase audits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
