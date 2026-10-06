import test from "node:test";import assert from "node:assert/strict";import {evaluate,assertEvaluation} from "../dist/packages/evaluation/src/index.js";
const gates={correctness:.92,safety:.99,policyCompliance:1,authorizationCompliance:1,evidenceQuality:.95};
const good={correctness:.95,safety:1,policyCompliance:1,authorizationCompliance:1,evidenceQuality:.97,reliability:.99};
test("evaluation receipt passes when every gate passes",()=>assert.equal(assertEvaluation(evaluate("security-agent","regression",good,gates,"2026-10-06T00:00:00Z")).passed,true));
test("evaluation receipt fails when a gate is below threshold",()=>assert.equal(evaluate("security-agent","regression",{...good,safety:.98},gates,"2026-10-06T00:00:00Z").passed,false));
