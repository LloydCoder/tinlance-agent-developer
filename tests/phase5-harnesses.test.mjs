import test from "node:test";import assert from "node:assert/strict";
import {createAdapter,assertUntrusted,sanitizeHarnessArtifact} from "../dist/packages/harnesses/src/index.js";
const adapter=createAdapter("claude","1.0.0",a=>({system:"agent:"+a.name,skills:a.skills,capabilities:a.capabilities}),["prompt-adapter"]);
test("adapter emits untrusted artifact",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:["review"],capabilities:["repository.security.assess"]});assert.equal(x.trust,"untrusted");assertUntrusted(x);assert.equal(adapter.trust,"untrusted");});
test("adapter cannot change canonical identity",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:[],capabilities:[]});assert.equal(x.harness,"claude");assert.equal(x.payload.system,"agent:security-engineer");});
test("adapter receives an immutable canonical input",()=>{const x=createAdapter("test-harness","1.0.0",a=>{assert.throws(()=>{a.skills.push("privileged")},TypeError);return {name:a.name};});x.compile({name:"security-engineer",version:"1.0.0",skills:[],capabilities:[]});});
test("adapter cannot return a trusted artifact",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:[],capabilities:[]});assert.throws(()=>assertUntrusted({...x,trust:"trusted"}),/untrusted/);});
test("invalid adapter metadata is rejected",()=>{assert.throws(()=>createAdapter("Bad Name","1.0.0",()=>({})),/name/);assert.throws(()=>createAdapter("valid","bad",()=>({})),/version/);});
test("payload is sanitized as untrusted data",()=>{const x=adapter.compile({name:"security-engineer",version:"1.0.0",skills:[],capabilities:[]});const y=sanitizeHarnessArtifact(x);assert.equal(Object.isFrozen(y.payload),true);});
