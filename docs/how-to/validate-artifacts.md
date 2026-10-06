# Validate and inspect artifacts

Use the TADL CLI to validate canonical artifacts without granting execution authority.

## Prerequisites

Run npm ci and npm run build from the repository root.

## Validate a schema-backed artifact

~~~bash
node cli/tadl.mjs validate capability/v1/capability.schema.json schemas/examples/security-assessment.capability.json
~~~

A valid artifact prints a JSON result containing "valid": true and exits with code 0.

## Inspect a capability

~~~bash
node cli/tadl.mjs capability inspect schemas/examples/security-assessment.capability.json
~~~

The command reports declared metadata, risk class, required authorizations, tools, approvals, and evidence.

## Validate a workflow

~~~bash
node cli/tadl.mjs workflow validate <workflow.json>
~~~

A valid workflow prints its deterministic compiled step order.

## Validate an agent

~~~bash
node cli/tadl.mjs agent validate <agent.json>
~~~

## Validate a skill

~~~bash
node cli/tadl.mjs skill validate <skill.json>
~~~

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Command completed successfully |
| 1 | Artifact validation failed |
| 2 | Unknown command, missing arguments, or unreadable input |

## Security boundary

CLI validation is not authorization. Passing validation does not grant tool access, secrets, sandbox privileges, policy approval, or execution authority.
