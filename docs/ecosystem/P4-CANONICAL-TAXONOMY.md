# P4 — Canonical Taxonomy Gate and Continuous Evolution

**Owner:** Agent OS catalog layer  
**Certification scope:** fail-closed validation of the 20K-scale canonical taxonomy release contract and the continuous-evolution invariants.  
**Status:** certified for repository-level taxonomy gate correctness. A real 20,000-entry published inventory is not claimed.

## Scope and invariants

1. Canonical semantic identity is based on normalized domain, capability set, and skill set—not display name, description, provider, model, locale, deployment mode, geography, or other variant metadata.
2. Semantic normalization uses Unicode NFKC, whitespace collapsing, case-folding, duplicate-token collapse, and collision-safe structured encoding.
3. Candidate ingestion, 10K/20K release gates, forensic audit, and continuous evolution share the same semantic identity rules.
4. Release manifests bind the full release-relevant inventory, including canonical IDs, exact display metadata, semantic identity, provenance references, review references, and lifecycle state.
5. Release manifests fail closed on malformed counts, coverage, digest, duplicate IDs, semantic duplicates, insufficient domain diversity, missing provenance, and missing review references.
6. Evolution release records require unique valid IDs, reviewed provenance, semantic uniqueness among active canonical entries, explicit deprecation transitions, normalized release identity, and SHA-256 digests.
7. Taxonomy metadata and release records never grant execution authority. Agent Platform remains the sole authority plane.

## Executable evidence

The cross-repository P4 gate runs the OS suites for:
- 20K expansion gate and GA semantics;
- 10K release gate;
- forensic inventory audit;
- candidate lifecycle and semantic deduplication;
- continuous evolution and deprecation;
- canonical taxonomy model and pipeline.

Regression coverage includes duplicate-token inflation, display-label renaming, case/whitespace normalization, delimiter collisions, malformed manifest values, incomplete evidence references, duplicate IDs, deterministic digest behavior, and order independence.

## Evidence boundary

The tests use synthetic fixtures to prove that the gates reject invalid inventories at scale. They do **not** prove that a real-world reviewed 20,000-entry inventory has been published. A real release claim requires an immutable persisted inventory artifact, verifiable per-entry source/review evidence, and an audit report bound to that exact artifact.

## P4 exit criteria

- [x] Agent OS implementation PR #134 is merged at `6a37934a2e602c6f31c2c6b943500af92d528f5b` after required checks passed.
- [x] TADL gate is pinned to the exact merged OS SHA and runs every P4-critical test suite.
- [x] The four-repository lock and manifest agree on all repository SHAs and the certified P4 state.
- [x] CI, security analysis, architecture checks, and ecosystem conformance are green.
- [x] Post-merge evidence is recorded against the exact merged revision.
- [x] The phase matrix and manifest are reconciled; P5 is the only next phase eligible to begin.

Repository certification is not production deployment certification.


## P4 post-merge certification evidence — 2026-10-17

**Agent OS implementation PR:** [#134](https://github.com/LloydCoder/tinlance-agent-os/pull/134)  
**Merged OS revision:** `6a37934a2e602c6f31c2c6b943500af92d528f5b`

Post-merge OS checks on the exact merged revision:
- CI: [39070315559](https://github.com/LloydCoder/tinlance-agent-os/actions/runs/39070315559) — success
- CodeQL: [39070315562](https://github.com/LloydCoder/tinlance-agent-os/actions/runs/39070315562) — success
- OpenSSF Scorecard: [39070315583](https://github.com/LloydCoder/tinlance-agent-os/actions/runs/39070315583) — success

**TADL candidate certification PR:** [#60](https://github.com/LloydCoder/tinlance-agent-developer/pull/60)  
**Merged TADL revision:** `a8815a13fd7c37047733bc3388130fa96215999a`

Post-merge TADL checks on the exact merged revision:
- CI: [39070717902](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717902) — success
- Ecosystem Integration: [39070717855](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717855) — success
- Security: [39070717984](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717984) — success
- Secret Scan: [39070717917](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717917) — success
- Release Attestations: [39070717893](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717893) — success
- OpenSSF Scorecard: [39070717883](https://github.com/LloydCoder/tinlance-agent-developer/actions/runs/39070717883) — success

The gate validates the correctness of the taxonomy release/evolution controls using synthetic fixtures. It does not claim that a real-world reviewed 20,000-entry inventory has been published. External production deployment remains unverified.
