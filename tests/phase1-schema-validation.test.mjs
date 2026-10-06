import test from "node:test";
import assert from "node:assert/strict";
import { validateAgainstSchema, validateArtifact } from "../packages/schemas/src/index.mjs";

const valid = {
  apiVersion: "tadl.tinlance.com/v1",
  kind: "Capability",
  metadata: { name: "repository.security.assess", version: "1.0.0" },
  risk: { class: "R1" },
  spec: { inputs: {}, outputs: {}, requires: { authorizations: ["repository.read"], tools: ["repository.inspect"], approvals: [], evidence: [] } }
};

test("valid capability passes canonical schema", () => assert.equal(validateArtifact("capability/v1/capability.schema.json", valid).valid, true));
test("invalid risk fails canonical schema", () => assert.equal(validateArtifact("capability/v1/capability.schema.json", {...valid, risk: {class: "R9"}}).valid, false));
test("unknown properties are rejected", () => assert.equal(validateArtifact("capability/v1/capability.schema.json", {...valid, unexpected: true}).valid, false));

test("2020-12 $ref resolves local JSON Pointers", () => {
  const schema = {$defs: {name: {type: "string", minLength: 3}}, properties: {name: {$ref: "#/$defs/name"}}, required: ["name"], type: "object"};
  assert.equal(validateAgainstSchema(schema, {name: "abc"}).valid, true);
  assert.equal(validateAgainstSchema(schema, {name: "x"}).valid, false);
});

test("2020-12 combinators are enforced", () => {
  const schema = {oneOf: [{type: "string"}, {type: "number"}]};
  assert.equal(validateAgainstSchema(schema, "ok").valid, true);
  assert.equal(validateAgainstSchema(schema, 42).valid, true);
  assert.equal(validateAgainstSchema(schema, true).valid, false);
});

test("array uniqueness and bounds are enforced", () => {
  const schema = {type: "array", minItems: 2, maxItems: 3, uniqueItems: true, items: {type: "integer"}};
  assert.equal(validateAgainstSchema(schema, [1, 2]).valid, true);
  assert.equal(validateAgainstSchema(schema, [1, 1]).valid, false);
  assert.equal(validateAgainstSchema(schema, [1]).valid, false);
});

test("format validation rejects malformed UUID", () => {
  assert.equal(validateAgainstSchema({type: "string", format: "uuid"}, "not-a-uuid").valid, false);
});

test("schema path traversal is rejected", () => {
  assert.throws(() => validateArtifact("../package.json", {}), /escapes schema root/);
});
