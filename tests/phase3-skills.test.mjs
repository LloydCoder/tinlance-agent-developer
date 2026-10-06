import test from "node:test";import assert from "node:assert/strict";import {assertSkill,dependencyOrder} from "../dist/packages/skills/src/index.js";
const a={manifest:{name:"base-security",version:"1.0.0",purpose:"base",dependencies:[],requiredCapabilities:[]},files:{"skill.yaml":"name: base-security","SKILL.md":"review"}};
const b={manifest:{name:"review",version:"1.0.0",purpose:"review",dependencies:["base-security"],requiredCapabilities:["repository.security.assess"]},files:{"skill.yaml":"name: review","SKILL.md":"review"}};
test("skill packages validate and freeze",()=>{const x=assertSkill(a);assert.equal(Object.isFrozen(x),true);});
test("dependencies resolve deterministically",()=>assert.deepEqual(dependencyOrder([b,a]),["base-security","review"]));
test("cycles are rejected",()=>{const x={...a,manifest:{...a.manifest,name:"cycle",dependencies:["cycle"]}};assert.throws(()=>dependencyOrder([x]),/cycle/);});
