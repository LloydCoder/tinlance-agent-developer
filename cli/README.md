# TADL CLI

The TADL CLI is the developer-facing contract surface. It validates artifacts and inspects declarative metadata; it never grants execution authority.

Commands:
- `tadl validate <schema> <artifact.json>`
- `tadl capability inspect <artifact.json>`
- `tadl workflow validate <workflow.json>`
- `tadl agent validate <agent.json>`
- `tadl skill validate <skill.json>`

All validation failures return exit code 1. Usage or command errors return exit code 2. Successful validation returns 0.
