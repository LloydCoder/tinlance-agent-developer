import test from "node:test";import assert from "node:assert/strict";import {ImmutableRegistry,RegistryError} from "../dist/packages/registry/src/index.js";
const a={kind:"Skill",name:"security-review",version:"1.0.0",digest:"sha256:"+"a".repeat(64),trust:"VERIFIED",payload:{purpose:"review"},publishedAt:"2026-10-06T00:00:00Z"};
test("registry publishes and resolves immutable versions",()=>{const r=new ImmutableRegistry();const p=r.publish(a);assert.equal(r.resolve("Skill","security-review","1.0.0"),p);assert.throws(()=>r.publish(a),RegistryError);});
test("revocation prevents resolution",()=>{const r=new ImmutableRegistry();r.publish(a);r.revoke("Skill","security-review","1.0.0");assert.throws(()=>r.resolve("Skill","security-review","1.0.0"),/revoked/);});
test("deprecation preserves artifact payload",()=>{const r=new ImmutableRegistry();r.publish(a);const d=r.deprecate("Skill","security-review","1.0.0");assert.equal(d.payload,a.payload);});
