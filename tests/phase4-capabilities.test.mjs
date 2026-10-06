import test from "node:test";import assert from "node:assert/strict";import {assertCapability,effectiveCapabilities,riskAtMost} from "../dist/packages/capabilities/src/index.js";
const read={name:"repository.security.assess",version:"1.0.0",risk:"R1",authorizations:["repository.read"],tools:["repository.inspect"],approvals:[],evidence:["repository.snapshot"],evaluation:{suite:"smoke",minimumScore:.92}};
const deploy={...read,name:"deployment.production.execute",risk:"R4",authorizations:["deployment.production"],tools:["deployment.write"],approvals:["human.production"],evidence:["deployment.attestation"]};
test("risk ordering is monotonic",()=>assert.equal(riskAtMost("R2","R4"),true));
test("declared capability is not effective without Platform authorization",()=>assert.equal(effectiveCapabilities([read],{authorizedCapabilities:[]}).length,0));
test("approval is required for high-risk capability",()=>assert.throws(()=>assertCapability({...deploy,approvals:[]}),/approval/));
test("authorized and approved capability becomes effective",()=>assert.equal(effectiveCapabilities([deploy],{authorizedCapabilities:[deploy.name],approvedCapabilities:[deploy.name]}).length,1));
