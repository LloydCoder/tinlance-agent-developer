import test from "node:test";
import assert from "node:assert/strict";
import {assertSkill,dependencyOrder,validateSkill} from "../dist/packages/skills/src/index.js";
const a={manifest:{name:"base-security",version:"1.0.0",purpose:"base",dependencies:[],requiredCapabilities:[]},files:{"skill.yaml":"name: base-security","SKILL.md":"review"}};
const b={manifest:{name:"review",version:"1.0.0",purpose:"review",dependencies:["base-security"],requiredCapabilities:["repository.security.assess"]},files:{"skill.yaml":"name: review","SKILL.md":"review"}};

test("skill packages validate and deeply freeze manifest collections",()=>{const x=assertSkill(a);assert.equal(Object.isFrozen(x),true);assert.equal(Object.isFrozen(x.manifest),true);assert.equal(Object.isFrozen(x.manifest.dependencies),true);assert.equal(Object.isFrozen(x.files),true);});
test("dependencies resolve deterministically regardless of input order",()=>{assert.deepEqual(dependencyOrder([b,a]),["base-security","review"]);assert.deepEqual(dependencyOrder([a,b]),["base-security","review"]);});
test("cycles are rejected",()=>{const x={...a,manifest:{...a.manifest,name:"cycle",dependencies:["cycle"]}};assert.throws(()=>dependencyOrder([x]),/cycle/);});
test("path traversal and unsupported package paths are rejected",()=>{const x={...a,files:{...a.files,"../escape":"x","notes.txt":"x"}};const errors=validateSkill(x);assert.ok(errors.some(e=>e.code==="PATH_INVALID"));assert.ok(errors.some(e=>e.code==="FILE_NOT_ALLOWED"));});
test("oversized files are rejected",()=>{const x={...a,files:{...a.files,"references/large":"x".repeat(1024*1024+1)}};assert.ok(validateSkill(x).some(e=>e.code==="FILE_TOO_LARGE"));});
test("malformed dependency metadata is rejected",()=>{const x={...a,manifest:{...a.manifest,dependencies:["Bad Name"]}};assert.ok(validateSkill(x).some(e=>e.code==="DEPENDENCY_INVALID"));});
