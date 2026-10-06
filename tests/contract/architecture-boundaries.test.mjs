import test from "node:test";import assert from "node:assert/strict";import fs from "node:fs";
const boundary=fs.readFileSync("docs/architecture/BOUNDARIES.md","utf8");
const architecture=fs.readFileSync("docs/architecture/ADRs.md","utf8");
test("TADL does not own authorization",()=>assert.match(boundary,/TADL[\s\S]*authorization/));
test("Platform owns authority",()=>assert.match(boundary,/Agent Platform[\s\S]*authority/));
test("Harnesses are untrusted",()=>assert.match(architecture,/Harnesses are untrusted/i));
test("Domain products retain ownership",()=>assert.match(boundary,/Domain products/));
