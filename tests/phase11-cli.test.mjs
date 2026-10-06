import test from "node:test";import assert from "node:assert/strict";import {spawnSync} from "node:child_process";
const run=(...args)=>spawnSync(process.execPath,["cli/tadl.mjs",...args],{encoding:"utf8"});
test("CLI help exits successfully",()=>{const r=run("help");assert.equal(r.status,0);assert.match(r.stdout,/tadl validate/);assert.match(r.stdout,/tadl workflow validate/);});
test("CLI validates the canonical example",()=>{const r=run("validate","capability/v1/capability.schema.json","schemas/examples/security-assessment.capability.json");assert.equal(r.status,0);assert.match(r.stdout,/valid/);});
test("capability inspect exposes governance metadata",()=>{const r=run("capability","inspect","schemas/examples/security-assessment.capability.json");assert.equal(r.status,0);assert.match(r.stdout,/repository.security.assess/);});
test("invalid command returns usage error",()=>{const r=run("does-not-exist");assert.equal(r.status,2);assert.match(r.stderr,/unknown command/);});
test("missing command arguments return usage error",()=>{const r=run("validate");assert.equal(r.status,2);});
test("skill validation routes through canonical schema",()=>{const file="schemas/examples/security-assessment.capability.json";const r=run("skill","validate",file);assert.equal(r.status,1);});
