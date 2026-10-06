# Security Policy

Report suspected vulnerabilities privately through GitHub security reporting.

## Non-negotiable invariants

- TADL MUST NOT grant execution authority.
- Skills MUST NOT directly authorize tools.
- Harness adapters are untrusted.
- Developer artifacts MUST NOT access raw secrets.
- Model output MUST NOT be treated as authoritative evidence.
- Learning MUST NOT modify authority.
- Privileged artifact promotion requires validation, evaluation, signing/provenance, and policy approval.
- Tenant boundaries MUST be preserved.

## Supply-chain controls

Workflow actions are pinned to full commit SHAs. Dependencies are installed with a committed lockfile and audited in CI. OpenSSF Scorecard is run on the public repository. Artifact provenance and signing primitives are included in the developer plane.

## Scope boundary

TADL is not the authorization, secret, sandbox, or governed execution plane. Those controls belong to Tinlance Agent Platform.
