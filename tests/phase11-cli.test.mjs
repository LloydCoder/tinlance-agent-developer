import test from "node:test";import assert from "node:assert/strict";import {spawnSync} from "node:child_process";
test("CLI help exits successfully",()=>{const r=spawnSync(process.execPath,["cli/tadl.mjs","help"],{encoding:"utf8"});assert.equal(r.status,0);assert.match(r.stdout,/tadl validate/);});
test("CLI validates the canonical example",()=>{const r=spawnSync(process.execPath,["cli/tadl.mjs","validate","capability/v1/capability.schema.json","schemas/examples/security-assessment.capability.json"],{encoding:"utf8"});assert.equal(r.status,0);assert.match(r.stdout,/valid/);});
