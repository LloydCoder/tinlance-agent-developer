import test from "node:test";import assert from "node:assert/strict";import {AgentLifecycle,validateAgent} from "../dist/packages/agents/src/index.js";
const p={name:"security-engineer",version:"1.0.0",purpose:"security review",skills:["review"],capabilities:["repository.security.assess"],maxRiskClass:"R1"};
test("agent lifecycle is explicit",()=>{const a=new AgentLifecycle(p);assert.equal(a.canExecute(),false);a.transition("VALIDATED");a.transition("PUBLISHED");assert.equal(a.canExecute(),true);a.transition("RETIRED");assert.equal(a.canExecute(),false);});
test("invalid agent profiles are rejected",()=>assert.ok(validateAgent({...p,capabilities:[]}).length>0));
