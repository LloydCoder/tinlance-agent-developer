import test from "node:test";import assert from "node:assert/strict";
import {acceptLearningProposal,authorityDigest} from "../dist/packages/evaluation/src/learning.js";
const authority={identity:{agent:"security-agent"},authorizations:{read:true},policies:{productionApproval:true},approvals:{required:true}};
const receipt={receiptVersion:"1",target:"security-agent",targetDigest:"sha256:"+"a".repeat(64),suite:"regression",suiteVersion:"1.0.0",caseCount:1,passedCases:1,metrics:{correctness:1,safety:1,policyCompliance:1,authorizationCompliance:1,evidenceQuality:1,reliability:1},gates:{correctness:.92,safety:.99,policyCompliance:1,authorizationCompliance:1,evidenceQuality:.95},passed:true,failures:[],modelVersion:"model-1",harnessVersion:"harness-1",toolVersions:{},environment:{},evaluatedAt:"2026-10-06T00:00:00Z"};
const base={id:"p1",target:"security-agent",behaviorDelta:{promptVersion:"2"},baselineAuthorityDigest:authorityDigest(authority),evaluationReceipt:receipt};
test("evaluated behavior proposal is accepted when current authority matches baseline",()=>assert.equal(acceptLearningProposal(base,authority).id,"p1"));
test("authority drift is rejected even when proposal carries the old digest",()=>assert.throws(()=>acceptLearningProposal(base,{...authority,policies:{productionApproval:false}}),/authority baseline/));
test("unevaluated proposals are rejected",()=>assert.throws(()=>acceptLearningProposal({...base,evaluationReceipt:{...receipt,passed:false}},authority),/evaluation/));
test("behavior delta is immutable after acceptance",()=>{const accepted=acceptLearningProposal(base,authority);assert.equal(Object.isFrozen(accepted.behaviorDelta),true);});
