# Security Policy

Report suspected vulnerabilities privately through GitHub security reporting.

## Non-negotiable invariants

- TADL MUST NOT grant execution authority.
- Skills MUST NOT directly authorize tools.
- Harness adapters are untrusted.
- Developer artifacts MUST NOT access raw secrets.
- Model output MUST NOT be treated as authoritative evidence.
- Learning MUST NOT modify authority.
- Privileged artifact promotion requires validation, evaluation, and policy approval.
- Tenant boundaries MUST be preserved.

Phase 0 establishes these requirements; later phases implement enforcement.
