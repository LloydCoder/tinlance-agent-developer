# Getting started

This tutorial gets a new contributor from a clean checkout to a verified TADL build.

## Prerequisites

- Git
- Node.js 22 or later
- npm

## 1. Clone the repository

~~~bash
git clone https://github.com/LloydCoder/tinlance-agent-developer.git
cd tinlance-agent-developer
~~~

## 2. Install dependencies

~~~bash
npm ci
~~~

The committed package-lock.json makes the dependency graph reproducible.

## 3. Build

~~~bash
npm run build
~~~

The build writes compiled TypeScript output to dist/.

## 4. Run the CLI

~~~bash
node cli/tadl.mjs help
~~~

## 5. Run the full verification gate

~~~bash
npm run ci
~~~

The gate checks structure and schemas, runs linting and compilation, executes tests, and runs the repository forensic audit.

## Next steps

- Read [Architecture](../explanation/architecture.md).
- Try [artifact validation](../how-to/validate-artifacts.md).
- Review the [CLI reference](../reference/cli.md).
- Read [CONTRIBUTING.md](../../CONTRIBUTING.md) before changing contracts.
