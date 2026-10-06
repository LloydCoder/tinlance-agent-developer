# Security Controls

- Least-privilege GitHub workflow permissions.
- Full SHA pinning for third-party workflow actions.
- Frozen npm dependency installation with a committed lockfile.
- High-severity dependency audit in CI.
- OpenSSF Scorecard scan.
- Immutable registry publication semantics.
- Explicit capability risk classes and approval/evidence declarations.
- Untrusted harness boundary.
- Ed25519 artifact signing and SLSA provenance predicate support.
- Learning proposals cannot change authority state.
- Tenant and execution authority remain outside TADL.

These controls align with current GitHub secure-use guidance and npm's lockfile/audit model.
