import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const files=[
"schemas/common/v1/common.schema.json","schemas/skill/v1/skill.schema.json",
"schemas/capability/v1/capability.schema.json","schemas/agent/v1/agent.schema.json",
"schemas/workflow/v1/workflow.schema.json","schemas/harness/v1/harness.schema.json",
"schemas/evaluation/v1/evaluation.schema.json","schemas/provenance/v1/provenance.schema.json",
"schemas/registry/v1/registry.schema.json"];
test("all Phase 0 schemas use JSON Schema 2020-12",()=>{
 for(const f of files){const s=JSON.parse(fs.readFileSync(f,"utf8"));assert.equal(s.$schema,"https://json-schema.org/draft/2020-12/schema",f);}
});
