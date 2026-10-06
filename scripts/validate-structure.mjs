import fs from "node:fs";

const required = [
  "docs/architecture/ARCHITECTURE.md","docs/architecture/BOUNDARIES.md",
  "docs/architecture/ADRs.md","docs/architecture/OWNERSHIP.md","docs/architecture/LIFECYCLE.md",
  "docs/security/README.md","docs/evaluation/README.md","docs/compatibility/README.md",
  "schemas/common/v1/common.schema.json","schemas/skill/v1/skill.schema.json",
  "schemas/capability/v1/capability.schema.json","schemas/agent/v1/agent.schema.json",
  "schemas/workflow/v1/workflow.schema.json","schemas/harness/v1/harness.schema.json",
  "schemas/evaluation/v1/evaluation.schema.json","schemas/provenance/v1/provenance.schema.json",
  "schemas/registry/v1/registry.schema.json",
  "packages/core/README.md","packages/schemas/README.md","packages/skills/README.md",
  "packages/capabilities/README.md","packages/agents/README.md","packages/workflows/README.md",
  "packages/harnesses/README.md","packages/evaluation/README.md","packages/registry/README.md",
  "packages/provenance/README.md","packages/security/README.md","packages/security/src/index.ts","tests/security/developer-boundary.test.mjs",".github/workflows/codeql.yml",".github/workflows/secrets.yml",".github/workflows/release-attestation.yml","cli/README.md"
];
for (const file of required) if (!fs.existsSync(file)) throw new Error(`Missing required path: ${file}`);
console.log(`Structure OK: ${required.length} required artifacts present.`);
