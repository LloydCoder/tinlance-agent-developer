import test from "node:test";import assert from "node:assert/strict";import {acceptLearningProposal} from "../dist/packages/evaluation/src/learning.js";
const base={id:"p1",target:"security-agent",behaviorDelta:{promptVersion:"2"},baselineAuthorityDigest:"sha256:aaa",proposedAuthorityDigest:"sha256:aaa",evaluationPassed:true};
test("evaluated behavior proposal is accepted when authority is unchanged",()=>assert.equal(acceptLearningProposal(base).id,"p1"));
test("authority changes are rejected",()=>assert.throws(()=>acceptLearningProposal({...base,proposedAuthorityDigest:"sha256:bbb"}),/authority/));
test("unevaluated proposals are rejected",()=>assert.throws(()=>acceptLearningProposal({...base,evaluationPassed:false}),/evaluation/));
