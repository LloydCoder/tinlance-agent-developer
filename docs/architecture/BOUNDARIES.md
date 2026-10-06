# Architectural Boundaries

| Layer | Owns | Must not own |
|---|---|---|
| TADL | skills, capability contracts, agent declarations, workflows, harness adapters, evaluation metadata, registry/provenance | authorization, secrets, sandbox authority, execution authority |
| Agent OS | workspace, sessions, tasks, lifecycle, orchestration, memory, channels, fleet | authorization authority, secret authority |
| Agent Platform | identity, authz, policy, approval, runtime, tools/MCP, sandbox, secrets, budgets, evidence, audit | domain semantics, developer package definitions |
| Domain products | domain entities, workflows, customer semantics | platform authority |

Immutable law: declared capability ∩ Platform authorization = effective capability.
