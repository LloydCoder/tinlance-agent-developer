# TADL CLI reference

The CLI is a local developer surface. It validates or inspects declarative artifacts; it does not grant execution authority.

## Invocation

After npm run build:

~~~bash
node cli/tadl.mjs <command>
~~~

The package also declares tadl as its binary entry point when the package is linked or installed from source.

## Commands

| Command | Purpose |
|---|---|
| tadl help | Print available commands |
| tadl validate <schema> <artifact.json> | Validate arbitrary JSON against a repository schema |
| tadl capability inspect <artifact.json> | Display capability governance metadata |
| tadl workflow validate <workflow.json> | Validate and compile a workflow |
| tadl agent validate <agent.json> | Validate an agent profile |
| tadl skill validate <skill.json> | Validate a skill against the canonical skill schema |

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Success |
| 1 | Validation failure |
| 2 | Usage or command error |

## Examples

~~~bash
node cli/tadl.mjs help
node cli/tadl.mjs validate capability/v1/capability.schema.json schemas/examples/security-assessment.capability.json
node cli/tadl.mjs capability inspect schemas/examples/security-assessment.capability.json
~~~

## Notes

The CLI's workflow and agent commands consume compiled package modules from dist/, so build first after a clean checkout.

Validation is deliberately separate from authorization and execution.
