<div align="center">

# Tinlance Agent Developer Layer (TADL)

**A declarative developer plane for packaging, validating, evaluating, signing, and distributing governed AI-agent artifacts.**

[![CI](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/ci.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/ci.yml)
[![Security](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/security.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/security.yml)
[![CodeQL](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/codeql.yml/badge.svg)](https://github.com/LloydCoder/tinlance-agent-developer/actions/workflows/codeql.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

</div>

> **Status:** v1.4.0 · public source repository · source installation only. TADL is not the execution-authority plane.

## Visual proof

~~~mermaid
flowchart LR
    D[Developer / Product] --> T[TADL]
    T --> O[Agent OS]
    O --> S[Platform SDK]
    S --> P[Agent Platform]
    P --> A[Governed execution authority]
    T --- SK[Skills]
    T --- CAP[Capabilities]
    T --- AG[Agents]
    T --- WF[Workflows]
    T --- EV[Evaluation]
    T --- PR[Provenance]
~~~

The diagram reflects the repository's architectural boundary: TADL declares and validates developer intent; Agent OS manages operational lifecycle; Agent Platform remains authoritative for authorization and governed execution.

## Why TADL

TADL is designed for teams that need a repeatable developer surface for governed AI agents without moving runtime authority into developer artifacts.

| Concern | TADL | Agent Platform |
|---|---|---|
| Skills and packaging | Owns | Consumes |
| Capability declarations | Owns declarations | Owns authorization |
| Agent profiles | Owns | Executes under policy |
| Workflow definitions | Validates/compiles | Governs consequential actions |
| Harness adapters | Defines untrusted boundary | Governs execution |
| Evaluation metadata | Owns developer-side artifacts | Provides authoritative evidence |
| Signing/provenance | Provides primitives | Enforces promotion/execution policy |
| Secrets, sandbox, budgets | Must not own | Owns |

**Core invariant:** declared capabilities ∩ Platform-authorized capabilities = effective capabilities.

## Quick Start

Prerequisites: Git and Node.js 22+.

~~~bash
git clone https://github.com/LloydCoder/tinlance-agent-developer.git
cd tinlance-agent-developer
npm ci
npm run build
node cli/tadl.mjs help
~~~

Run the complete repository gate:

~~~bash
npm run ci
~~~

The CI command validates structure and schemas, validates the four-repository ecosystem manifest and lock, runs linting, compiles TypeScript, executes tests, and runs the repository forensic audit.

## Installation

TADL is currently developed and distributed from source; package.json deliberately marks the package as private, so there is no npm-install command for a published package.

### From Git

~~~bash
git clone https://github.com/LloydCoder/tinlance-agent-developer.git
cd tinlance-agent-developer
npm ci
npm run build
~~~

### From an existing checkout

~~~bash
npm ci
npm run build
~~~

### Requirements

| Requirement | Supported baseline |
|---|---|
| Node.js | 22+ |
| npm | npm compatible with Node.js 22 |
| OS | Linux, macOS, or Windows with Git/Node available |
| Package manager | npm |
| TypeScript | 7.0.2 via the committed lockfile |

## Usage

TADL currently exposes validation and inspection commands through cli/tadl.mjs.

### Show the command surface

~~~bash
node cli/tadl.mjs help
~~~

### Validate an artifact against a schema

~~~bash
node cli/tadl.mjs validate capability/v1/capability.schema.json schemas/examples/security-assessment.capability.json
~~~

### Inspect capability governance metadata

~~~bash
node cli/tadl.mjs capability inspect schemas/examples/security-assessment.capability.json
~~~

### Validate a workflow or agent

~~~bash
node cli/tadl.mjs workflow validate <workflow.json>
node cli/tadl.mjs agent validate <agent.json>
~~~

Successful validation returns exit code 0; validation failures return 1; invalid commands or missing required arguments return 2.

## Configuration / Options

TADL is currently a source-level developer layer rather than a long-running service.

| Surface | Default | Notes |
|---|---|---|
| Node runtime | 22+ | Declared by package.json |
| Build output | dist/ | Produced by npm run build |
| Schemas | schemas/ | Canonical repository schema tree |
| CLI | cli/tadl.mjs | Uses built package modules where required |
| Test runner | Node built-in test runner | npm test |
| CI gate | npm run ci | Structure → schemas → lint → build → tests → forensic audit |
| Package publication | Disabled | package.json sets private=true |

## Features

| Feature | What it provides |
|---|---|
| Canonical schemas | Versioned JSON Schema 2020-12 artifact contracts |
| Skills | Immutable skill-package validation and dependency ordering |
| Capabilities | Risk-classified capability declarations and effective-capability calculation |
| Agents | Versioned profiles and explicit lifecycle states |
| Workflows | Declarative DAG validation and deterministic compilation |
| Harnesses | Untrusted adapter boundary |
| Evaluation | Case-level results, aggregate gates, receipts, and constrained learning |
| Registry | Append-only publication/deprecation/revocation semantics |
| Provenance | Canonical SHA-256 digests, Ed25519 signatures, SLSA/in-toto primitives |
| Security | Developer-artifact authority/secret boundary checks |
| CLI | Local artifact validation and governance inspection |
| Supply chain | Locked dependencies, pinned Actions, CodeQL, secret scanning, SBOM, attestations |

## Documentation

### Diátaxis map

- **Tutorial:** [Getting started](docs/tutorials/getting-started.md)
- **How-to:** [Validate and inspect artifacts](docs/how-to/validate-artifacts.md)
- **Explanation:** [Architecture](docs/explanation/architecture.md)
- **Reference:** [CLI reference](docs/reference/cli.md)
- [Architecture boundaries](docs/architecture/BOUNDARIES.md)
- [Lifecycle](docs/architecture/LIFECYCLE.md)
- [Security controls](docs/security/CONTROLS.md)
- [Threat model](docs/security/THREAT-MODEL.md)
- [Compatibility](docs/compatibility/README.md)
- [P0 ecosystem forensic baseline](docs/ecosystem/P0-BASELINE.md)
- [P1 Transformation model](docs/architecture/PHASE-14-TRANSFORMATION.md)
- [Machine-readable ecosystem manifest](docs/ecosystem/ecosystem-manifest.json)
- [Ecosystem release lock](ecosystem.lock.json)
- [Ecosystem conformance](docs/integration/CONFORMANCE.md)
- [Phase documentation](docs/architecture/)
- [LLM-oriented documentation map](llms.txt)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Changes that affect schemas, risk classes, lifecycle, authority boundaries, or compatibility require corresponding documentation and tests.

## License + Acknowledgements

TADL is licensed under the [Apache License 2.0](LICENSE).

The project uses TypeScript and Node.js, GitHub Actions, OpenSSF Scorecard, CodeQL, Gitleaks, CycloneDX SBOM generation, and GitHub artifact attestations as part of its development and supply-chain controls.

<details>
<summary>Roadmap</summary>

The defined engineering phases 0–13 are implemented in the repository, including Phase 13 enterprise hardening. Future work should extend contracts without moving execution authority into TADL.

</details>

<details>
<summary>Troubleshooting</summary>

If a command fails after cloning, run:

~~~bash
node --version
npm --version
npm ci
npm run build
npm run ci
~~~

If the CLI cannot find built modules, run npm run build before invoking commands that consume dist/.

</details>

<details>
<summary>Support</summary>

For usage questions and project guidance, see [SUPPORT.md](SUPPORT.md). Security issues must follow [SECURITY.md](SECURITY.md) and should not be reported in public issues.

</details>
