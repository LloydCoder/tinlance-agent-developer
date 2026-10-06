# Release Policy

1. Run the complete CI and Security workflows.
2. Run the forensic audit.
3. Review schema/API compatibility and SemVer impact.
4. Ensure published artifacts are immutable and signed.
5. Record evaluation receipts and provenance.
6. Tag the release only from a green protected main branch.

No release may silently alter capability risk, authorization requirements, evidence requirements, or trust semantics.
