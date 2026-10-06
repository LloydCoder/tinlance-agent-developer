# Architectural Boundaries

| Concern | TADL | Agent OS | Agent Platform | Domain products |
|---|---:|---:|---:|---:|
| Skills | OWN | consume | govern | may publish |
| Capabilities | OWN contract | request | AUTHORIZE | domain-specific |
| Agents | OWN declaration | lifecycle | authorize | compose |
| Workflows | OWN definition | EXECUTE | govern actions | domain workflows |
| Identity | NO | consume | OWN | consume |
| Authorization | NO | NO | OWN | consume |
| Sandbox | NO | request | OWN | consume |
| Secrets | NO | request | OWN | consume |
| Evidence authority | define expectations | organize | OWN | consume |
| Domain semantics | NO | NO | NO | OWN |

No package may create a second authority path.
