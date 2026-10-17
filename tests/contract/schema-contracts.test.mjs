import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { validateArtifact } from "../../packages/schemas/src/index.mjs";

const files=[
"schemas/common/v1/common.schema.json","schemas/skill/v1/skill.schema.json",
"schemas/capability/v1/capability.schema.json","schemas/agent/v1/agent.schema.json",
"schemas/workflow/v1/workflow.schema.json","schemas/harness/v1/harness.schema.json",
"schemas/evaluation/v1/evaluation.schema.json","schemas/provenance/v1/provenance.schema.json",
"schemas/registry/v1/registry.schema.json","schemas/transformation/v1/transformation.schema.json"];
test("all Phase 0 schemas use JSON Schema 2020-12",()=>{
 for(const f of files){const s=JSON.parse(fs.readFileSync(f,"utf8"));assert.equal(s.$schema,"https://json-schema.org/draft/2020-12/schema",f);}
});


test("P1 transformation example conforms to the canonical schema", () => {
  const example = JSON.parse(fs.readFileSync("schemas/examples/transformation.v1.json", "utf8"));
  const result = validateArtifact("transformation/v1/transformation.schema.json", example);
  assert.equal(result.valid, true, JSON.stringify(result.errors));
});

test("P1 transformation requires provenance and rejects contradictory achieved outcomes", () => {
  const example = JSON.parse(fs.readFileSync("schemas/examples/transformation.v1.json", "utf8"));
  const withoutProvenance = { ...example };
  delete withoutProvenance.provenance;
  assert.equal(
    validateArtifact("transformation/v1/transformation.schema.json", withoutProvenance).valid,
    false
  );
  const contradictory = {
    ...example,
    outcome: { ...example.outcome, status: "achieved", achieved: false }
  };
  assert.equal(
    validateArtifact("transformation/v1/transformation.schema.json", contradictory).valid,
    false
  );
});


test("canonical ecosystem phase map uses the approved P0-P10 sequence", () => {
  const matrix = fs.readFileSync("docs/ecosystem/PHASE-MATRIX.md", "utf8");
  const expected = [
    "P0 | Forensic baseline and reconciliation",
    "P1 | Canonical contracts",
    "P2 | Identity, tenancy, authentication and authorization",
    "P3 | Event delivery and durability",
    "P4 | Trace context and evidence lineage",
    "P5 | Registries and lifecycle governance",
    "P6 | Model/tool routing and mediation",
    "P7 | Real adapters and integration boundaries",
    "P8 | Budgets, quotas, capacity and cost enforcement",
    "P9 | MCP/A2A interoperability and security",
    "P10 | End-to-end recovery and production certification",
  ];
  for (const scope of expected) assert.ok(matrix.includes(scope), `missing canonical scope: ${scope}`);
  assert.ok(matrix.includes("not, by themselves, certification of a similarly numbered canonical ecosystem phase"));
  const manifest = JSON.parse(fs.readFileSync("docs/ecosystem/ecosystem-manifest.json", "utf8"));
  assert.equal(manifest.certification_state.sequence, "ecosystem-p0-p10");
  assert.equal(manifest.certification_state.production, "unverified");
});
