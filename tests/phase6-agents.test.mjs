import test from "node:test";import assert from "node:assert/strict";
import {AgentLifecycle,validateAgent} from "../dist/packages/agents/src/index.js";
const p={name:"security-engineer",version:"1.0.0",purpose:"security review",skills:["review"],capabilities:["repository.security.assess"],maxRiskClass:"R1"};
const evidence={artifactDigest:"sha256:"+"a".repeat(64),evaluationReceiptId:"eval-1",evaluationPassed:true,provenanceDigest:"sha256:"+"b".repeat(64),signature:"signed-receipt",publishedAt:"2026-10-06T00:00:00Z"};
test("agent lifecycle requires publication evidence",()=>{const a=new AgentLifecycle(p);assert.equal(a.canExecute(),false);a.transition("VALIDATED");assert.throws(()=>a.transition("PUBLISHED"),/publication evidence/);a.transition("PUBLISHED",evidence);assert.equal(a.canExecute(),true);a.transition("RETIRED");assert.equal(a.canExecute(),false);});
test("publication requires passing evaluation and integrity metadata",()=>{const a=new AgentLifecycle(p);a.transition("VALIDATED");assert.throws(()=>a.transition("PUBLISHED",{...evidence,evaluationPassed:false}),/passing evaluation/);assert.throws(()=>a.transition("PUBLISHED",{...evidence,artifactDigest:"bad"}),/artifact digest/);});
test("invalid agent profiles are rejected",()=>assert.ok(validateAgent({...p,capabilities:[]}).length>0));
test("agent profile collections are immutable",()=>{const a=new AgentLifecycle(p);assert.equal(Object.isFrozen(a.profile.skills),true);assert.equal(Object.isFrozen(a.profile.capabilities),true);});
