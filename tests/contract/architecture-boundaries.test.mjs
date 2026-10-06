import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("TADL is not the execution authority",()=>{
  const b=fs.readFileSync("docs/architecture/BOUNDARIES.md","utf8");
  assert.match(b,/Agent Platform/);
  assert.match(b,/Authorization.*NO.*OWN/);
});
test("harness trust is untrusted",()=>{
  const s=JSON.parse(fs.readFileSync("schemas/harness/v1/harness.schema.json","utf8"));
  assert.equal(s.properties.spec.properties.trust.const,"untrusted");
});
test("risk taxonomy is R0-R5",()=>{
  const s=JSON.parse(fs.readFileSync("schemas/capability/v1/capability.schema.json","utf8"));
  assert.deepEqual(s.properties.risk.properties.class.enum,["R0","R1","R2","R3","R4","R5"]);
});
