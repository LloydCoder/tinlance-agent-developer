# TADL Internal Phase 0 — Architecture Foundation


> **Phase namespace:** This is the TADL repository's internal implementation sequence. It is not the ecosystem certification phase with the same number in `docs/ecosystem/PHASE-MATRIX.md`. Ecosystem P0–P10 gates cross repository boundaries and are authoritative for release sequencing.

## Objectives

- Freeze ownership and authority boundaries.
- Establish the complete repository topology.
- Establish contract/versioning rules.
- Establish security and trust invariants.
- Establish machine-checkable CI gates.
- Establish safe examples and test scaffolding.

## Exit criteria

- Required repository topology exists.
- All Phase 0 schemas parse and declare JSON Schema 2020-12.
- Boundary tests pass.
- Structure validation passes.
- Lint passes.
- TypeScript build passes.
- CI workflow completes successfully.
- No production execution authority exists in TADL.

## Deferred

Production skill runtime, capability enforcement, agent runtime, workflow execution, harness implementations, registry service, signing, and adversarial evaluation belong to later phases.
