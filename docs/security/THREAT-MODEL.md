# TADL Phase 0 Threat Model

## Untrusted inputs

Skills, agent instructions, workflow input, model output, harness events, MCP metadata, memory, external documentation, tool output, and customer repository content are untrusted.

## Threats

- Prompt/skill injection
- Malicious dependency or package substitution
- Capability confusion
- Authority escalation
- Approval manipulation
- Secret exfiltration
- Evidence fabrication
- Provenance forgery
- Version confusion
- Tenant escape
- Harness compromise

## Required control

No untrusted artifact can independently grant authority. Agent Platform remains the sole execution authority.
