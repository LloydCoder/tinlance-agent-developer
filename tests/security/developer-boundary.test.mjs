import test from "node:test";import assert from "node:assert/strict";
import {scanDeveloperArtifact,assertDeveloperArtifactSafe,assertAuthoritySeparation} from "../../dist/packages/security/src/index.js";
test("developer artifacts cannot define authority fields",()=>{const findings=scanDeveloperArtifact({name:"skill",permissions:["deploy"]});assert.ok(findings.some(f=>f.code==="AUTHORITY_FIELD"&&f.severity==="CRITICAL"));assert.throws(()=>assertDeveloperArtifactSafe({authorization:"grant"}),/AUTHORITY_FIELD/);});
test("secret-like values are rejected",()=>{const findings=scanDeveloperArtifact({prompt:"Bearer abcdefghijklmnopqrstuvwxyz"});assert.ok(findings.some(f=>f.code==="SECRET_LIKE_VALUE"));assert.throws(()=>assertDeveloperArtifactSafe({token:"ghp_"+ "A".repeat(30)}),/SECRET_LIKE_VALUE/);});
test("safe developer artifacts pass",()=>assert.doesNotThrow(()=>assertDeveloperArtifactSafe({name:"review",purpose:"read-only security analysis",capabilities:["repository.security.assess"]})));
test("effective authority is an intersection, never a union",()=>assert.deepEqual(assertAuthoritySeparation(["read","write"],["read"]),["read"]));
