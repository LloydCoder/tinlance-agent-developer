# P9 — Reference Enterprise Certification

P9 proves that the Agent System can describe a complete enterprise workforce
without turning workforce metadata into authority.

## Reference workforce

The locked Platform reference workforce contains eleven deterministic roles:

1. Executive
2. Research
3. Finance
4. Security
5. Engineering
6. Sales
7. Marketing
8. Operations
9. Customer Success
10. Procurement
11. Compliance

Each role has a stable identifier, business function, mission, capability
vocabulary, and explicit human escalation target.

## Security boundary

A workforce role is a descriptive composition. Role names, capabilities,
catalog metadata, model output, escalation metadata, and workforce fixtures
cannot authorize an action.

Consequential work must traverse:

`human/workload identity → agent identity → tenant → capability → policy →
risk → approval → budget → sandbox/tool authority → execution → evidence`

The Platform remains the sole consequential authority plane.

## Operational composition

The reference workforce is designed to compose through Agent OS workspaces,
tasks, workflows, teams, memory, knowledge and channels. The Platform governs
all consequential execution, approvals, secrets, budgets, sandboxing, tool/MCP
access and authoritative evidence.

The workforce is intentionally deterministic so that the same system contracts
can be parameterized for independent tenants during P10 replication.

## Acceptance evidence

P9 is accepted only when:

- all eleven roles exist exactly once;
- role IDs are stable and canonical;
- capabilities are unique within each role;
- serialized profiles contain descriptive data only;
- workforce tests and contract-boundary tests pass;
- the full ecosystem phase certification passes.

P9 does not claim that an external enterprise has been deployed. It certifies
the reusable reference composition contained in the repositories.
