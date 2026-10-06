import test from "node:test";import assert from "node:assert/strict";import {createAdapter,assertUntrusted} from "../dist/packages/harnesses/src/index.js";
const adapter=createAdapter("claude","1.0.0",a=>({system:"agent:"+a.name,skills:a.skills,capabilities:a.capabilities}));
test("adapter emits untrusted artifact",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:["review"],capabilities:["repository.security.assess"]});assert.equal(x.trust,"untrusted");assertUntrusted(x);});
test("adapter cannot change canonical identity",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:[],capabilities:[]});assert.equal(x.harness,"claude");assert.equal(x.payload.system,"agent:security-engineer");});
