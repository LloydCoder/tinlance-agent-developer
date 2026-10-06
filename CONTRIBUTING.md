# Contributing to TADL

Thank you for contributing to the Tinlance Agent Developer Layer (TADL).

## Before you start

Read [Architecture boundaries](docs/architecture/BOUNDARIES.md), [Lifecycle](docs/architecture/LIFECYCLE.md), [Security controls](docs/security/CONTROLS.md), and [Compatibility](docs/compatibility/README.md).

TADL is a developer plane. Contributions must not move authorization, secrets, sandbox enforcement, execution authority, or authoritative evidence into TADL.

## Development flow

1. Fork the repository.
2. Create a focused branch from main.
3. Make the smallest coherent change.
4. Add or update tests for behavior changes.
5. Update documentation when a contract, CLI command, security invariant, or user-visible behavior changes.
6. Run npm ci.
7. Run npm run ci.
8. Open a pull request using the repository template.

Do not commit directly to main.

## Coding standards

- TypeScript uses strict compiler settings.
- Preserve ESM/NodeNext conventions.
- Keep public contracts explicit and versioned.
- Prefer deterministic behavior and immutable artifacts.
- Fail closed on invalid trust, authorization, provenance, or contract state.
- Do not introduce secrets, credentials, tokens, or customer data into fixtures.
- Do not weaken existing security checks to make tests pass.

## Tests

~~~bash
npm test
npm run ci
~~~

The full gate must pass before requesting review.

## Contract changes

Schema, risk-class, lifecycle, compatibility, provenance, security-boundary, or authority-ownership changes require an ADR or ADR update, corresponding tests, documentation, and compatibility impact analysis.

## Commits

Use Conventional Commit-style messages such as:

~~~text
feat: add artifact inspection command
fix: reject invalid provenance envelope
docs: clarify workflow validation
test: cover registry tamper detection
chore: update dependency lockfile
~~~

Keep commits small and logically grouped.

## Pull requests

Explain what changed, why it changed, affected contracts, security implications, compatibility implications, and tests performed. Avoid unrelated formatting or refactoring.

## Security issues

Do not open a public issue for a suspected vulnerability. Follow [SECURITY.md](SECURITY.md).

## Maintainer ownership

The repository currently has a single defined CODEOWNER, @LloydCoder. Update CODEOWNERS when additional maintainers or teams become responsible for specific areas.
