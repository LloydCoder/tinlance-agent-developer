# P5 Post-Merge Forensic Audit

**Disposition:** post-merge audit candidate; P5 certification remains in progress until this branch's exact-SHA workflows pass.  
**Baseline:** `ecosystem-p5-postmerge-audit-candidate-2026-10-18`  
**Audit date:** 2026-10-18  
**Production readiness:** unverified; no production deployment or live operational telemetry is certified by these repository checks.

## Scope and authority boundaries

P5 upgrades the canonical ecosystem registry to TSIC-owned `registry-manifest/v2`, while preserving v1 as an immutable deprecated contract with an explicit active v2 replacement. The registry records publisher identity state, resource lifecycle state, exact reviewed revisions, provenance references, SBOM/signature attestation-index references, and explicit supply-chain verification state.

The registry is descriptive metadata, not an execution grant. The Platform remains the sole consequential execution authority; the OS owns orchestration and lifecycle; the SDK remains a typed client contract; TADL validates developer artifacts and registry conformance; TSIC remains the system-of-systems contract and certification authority.

## Exact reviewed baseline

| Component | Reviewed SHA | Evidence |
|---|---|---|
| TADL | `e31cf6ab2a9b5702067711adaf85099812cf10d4` | P5 implementation merge commit; post-merge audit updates the lock to this immutable revision |
| Agent OS | `62826433a3110f7d29fd8dc7295efa584fa7934e` | Exact lock pin exercised by ecosystem integration |
| Agent Platform | `34912c0640c186ba8fc5b92bdd98ec3a1704ce0d` | [P5 merge](https://github.com/LloydCoder/tinlance-agent-platform/commit/34912c0640c186ba8fc5b92bdd98ec3a1704ce0d) |
| Platform SDK | `2f358d5dd1e562918613f138b7ef1e3a16f693cb` | Exact lock pin exercised by ecosystem integration |
| TSIC authority | `e98613c56c7cc52e063557987bb5436cfb24d207` | [Registry v2 schema/contract merge](https://github.com/LloydCoder/tinlance-system-integration/commit/e98613c56c7cc52e063557987bb5436cfb24d207) |

## Merge and workflow evidence

- **TSIC PR #74** merged the v2 registry schema and contract. Its schema/contract conformance checks passed before merge.
- **Platform PR #113** merged at `34912c0640c186ba8fc5b92bdd98ec3a1704ce0d`. Main-push CI #1152, R10 Certification #458, CodeQL #771, Reference Agents #813, and Supply Chain Attestation succeeded. The [CI run](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39106681204), [R10 run](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39106681172), [CodeQL run](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39106681178), [Reference Agents run](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39106681192), and [attestation run](https://github.com/LloydCoder/tinlance-agent-platform/actions/runs/39106681210) are linked for inspection.
- **TADL PR #71** merged at `e31cf6ab2a9b5702067711adaf85099812cf10d4`. Post-merge Secret Scan #278, Security #308, CodeQL #279, Ecosystem Integration #266, and Supply Chain Attestation succeeded. The [post-merge integration run](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39106820022), [CodeQL run](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39106819928), and [attestation run](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39106819824) are linked for inspection.
- The PR-head integration gate also passed against the exact merged Platform SHA, including TSIC schema parity, P2 identity/tenancy, P3 event delivery, P4 trace/evidence lineage, component regression, and P5 registry conformance.

## P5 controls exercised

- Exact repository SHA, role, and baseline parity across lock, manifest, and registry.
- Local registry v2 schema byte/structure parity with the pinned TSIC authority and presence of the canonical v2 contract.
- Immutable v1 deprecation and active v2 replacement; active services and required agents cannot consume deprecated contracts.
- Publisher identity URI bound to publisher ID; provenance URI bound to the exact reviewed GitHub commit; SBOM/signature references bound to the repository attestation index.
- Lifecycle replacement targets must exist and be active; quarantined resources must be disabled; revoked publisher/supply-chain states fail closed when active resources depend on them.
- Negative controls for missing SBOM reference, stale reviewed SHA, wrong provenance SHA, mismatched publisher identity, revoked publisher, revoked supply-chain evidence, active quarantined service, active use of deprecated v1, and missing active replacement.

## Residuals deliberately deferred to P10

- Platform and TADL main-branch provenance/SBOM attestations were generated successfully, but the registry status remains `pending` until P10 independently verifies each attestation's signature, predicate, subject digest, repository, and reviewed SHA.
- Agent OS, Platform SDK, and TSIC still need their own reproducible attestation generation and verification evidence before supply-chain status can be upgraded.
- No production deployment, production secrets, live external adapters, or production telemetry are certified by this P5 repository/CI audit.

## Current phase state

P0-P4 are certified for the reviewed exact-SHA scope. P5 remains `in_progress` while this post-merge baseline's CI and conformance gates run. P6-P10 remain `not_started`; production readiness remains `unverified`.
