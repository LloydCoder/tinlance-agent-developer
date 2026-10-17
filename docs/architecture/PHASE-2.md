# TADL Internal Phase 2 — Artifact Registry


> **Phase namespace:** This is the TADL repository's internal implementation sequence. It is not the ecosystem certification phase with the same number in `docs/ecosystem/PHASE-MATRIX.md`. Ecosystem P0–P10 gates cross repository boundaries and are authoritative for release sequencing.

Phase 2 establishes the registry contract: immutable publication, exact version resolution, trust metadata, deprecation, revocation, and append-only state transitions. A production registry service may persist this contract later; it must not weaken immutability or trust semantics.
