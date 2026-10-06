import test from "node:test";import assert from "node:assert/strict";import {compileWorkflow,validateWorkflow} from "../dist/packages/workflows/src/index.js";
const w={name:"security-review",version:"1.0.0",steps:[{id:"report",capability:"report.create",dependsOn:["assess"],evidence:[]},{id:"assess",capability:"repository.security.assess",dependsOn:[],evidence:["snapshot"]}]};
test("workflow compiler produces deterministic topological order",()=>assert.deepEqual(compileWorkflow(w).order,["assess","report"]));
test("workflow cycles are rejected",()=>assert.throws(()=>compileWorkflow({...w,steps:[{...w.steps[0],dependsOn:["report"]},w.steps[1]]}),/cycle/));
test("production steps require approval metadata",()=>assert.ok(validateWorkflow({...w,steps:[{...w.steps[0],capability:"deployment.production.execute"}]}).length>0));
