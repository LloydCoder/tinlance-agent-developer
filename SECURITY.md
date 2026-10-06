# Security Policy

TADL treats developer artifacts, model output, workflow input, harness events, MCP metadata, memory, external documentation, tool output, and customer repository content as untrusted.

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub issues, pull requests, or discussions.**

Preferred channel:

1. Open the repository's **Security** tab.
2. Choose **Report a vulnerability** and submit a private vulnerability report.

Direct advisory entry point: https://github.com/LloydCoder/tinlance-agent-developer/security/advisories/new

If private vulnerability reporting is not enabled, contact **@LloydCoder** privately through GitHub and include enough information to reproduce the issue without publishing sensitive details.

Private vulnerability reporting is a repository setting and is separate from this SECURITY.md policy.

## What to include

Provide the affected version or commit, vulnerability description, security impact, reproduction steps or proof of concept, relevant logs with secrets removed, and proposed mitigation if known.

## Response targets

These are maintainer response targets, not guaranteed service levels.

| Stage | Target |
|---|---|
| Initial acknowledgement | Within 3 business days |
| Initial triage/severity assessment | Within 7 business days |
| Remediation plan | Within 14 business days where practical |
| Coordinated disclosure | Agreed with the reporter based on severity and patch availability |

Critical issues may be handled immediately and outside these targets.

## Security invariants

- TADL MUST NOT grant execution authority.
- Skills MUST NOT directly authorize tools.
- Harness adapters are untrusted.
- Developer artifacts MUST NOT contain raw secrets or credentials.
- Model output MUST NOT be treated as authoritative evidence.
- Learning MUST NOT modify authority.
- Privileged artifact promotion requires validation, evaluation, signing/provenance, and policy approval.
- Tenant boundaries remain outside TADL and are enforced by the appropriate platform layer.

## Supply-chain controls

The repository uses a committed npm lockfile, high-severity npm audit, full SHA pinning for GitHub Actions, CodeQL, secret scanning, OpenSSF Scorecard, CycloneDX SBOM generation, and GitHub artifact attestations.

## Scope boundary

TADL is not the authorization, secret, sandbox, or governed execution plane. Those controls belong to Tinlance Agent Platform.

See [Architecture Boundaries](docs/architecture/BOUNDARIES.md) and [Threat Model](docs/security/THREAT-MODEL.md).
