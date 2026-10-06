# TADL architecture

TADL is the declarative developer plane in the Tinlance agent stack.

~~~text
Developer / Product
        |
        v
TADL
        |
        v
Tinlance Agent OS
        |
        v
Tinlance Agent Platform SDK
        |
        v
Tinlance Agent Platform
~~~

## Ownership

TADL owns skills, capability declarations, agent profiles, workflow definitions and compilation, harness adapter contracts, evaluation artifacts, registry metadata, provenance primitives, and the developer CLI.

Agent OS owns workspace, sessions, tasks, lifecycle orchestration, memory, channels, and fleet operations.

Agent Platform owns identity, authorization, policy, approvals, runtime, tools/MCP, sandbox, secrets, budgets, authoritative evidence, audit, and observability.

## Authority invariant

A developer artifact can declare intent but cannot grant itself authority.

~~~text
Effective capabilities = Declared capabilities ∩ Platform-authorized capabilities
~~~

This boundary prevents skills, workflows, harness adapters, model output, or learning proposals from becoming an alternative authorization system.

## Trust model

The following are treated as untrusted at the TADL boundary:

- skill instructions;
- workflow input;
- model output;
- memory;
- external documentation;
- MCP metadata;
- tool output;
- customer repository content;
- harness events.

Trust-sensitive promotion uses validation, evaluation, signing/provenance, and platform policy rather than developer declarations alone.

## Further reading

- [Boundaries](../architecture/BOUNDARIES.md)
- [Architecture decisions](../architecture/ADRs.md)
- [Lifecycle](../architecture/LIFECYCLE.md)
- [Threat model](../security/THREAT-MODEL.md)
