# P1 — Ecosystem Transformation Certification

**Baseline:** `p1-2026-10-07`

## Certified repository revisions

| Plane | Reviewed revision |
|---|---|
| TADL / developer | `7eb4580940a4486b71be1f9a517e9b11af0a4f1c` |
| Agent OS | `46b12523d769b9145fb4ef5f0c80cad56f06ae7a` |
| Platform SDK | `798251e1927a5cbda1bcc03fd13f85eb7c90d2ea` |
| Agent Platform | `b32d2615668f07cf25dd98c82bbc5ae939070ebd` |

## Certified contract

`transformation/v1`

The Transformation spans:

`TADL declaration → OS lifecycle/context → SDK typed transport → Platform governance/execution → evidence → outcome`

The four implementations intentionally differ by ownership:

- TADL owns the canonical wire schema and declaration example.
- Agent OS owns lifecycle/context composition.
- SDK owns the typed developer transport surface.
- Agent Platform owns the authoritative execution-side contract and security boundary.

No implementation treats Transformation data as an authorization grant.

## P1 acceptance

P1 is certified only after all four repository PRs were individually green and merged, and this ecosystem baseline validates against their merged revisions.

P2 must not start until this certification branch itself passes the complete TADL CI/security/ecosystem gate.
