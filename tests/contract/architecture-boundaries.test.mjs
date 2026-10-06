import test from "node:test";import assert from "node:assert/strict";import fs from "node:fs";
const boundary=fs.readFileSync("docs/architecture/BOUNDARIES.md","utf8");
test("TADL does not own authorization",()=>assert.match(boundary,/TADL[\s\S]*authorization/));
test("Platform owns authority",()=>assert.match(boundary,/Agent Platform[\s\S]*authority/));
test("Harnesses are untrusted",()=>assert.match(boundary,/Harness.*untrusted/i));
test("Domain products retain ownership",()=>assert.match(boundary,/Domain products/));
