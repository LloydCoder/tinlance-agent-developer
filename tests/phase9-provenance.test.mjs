import test from "node:test";import assert from "node:assert/strict";import {generateKeyPairSync} from "node:crypto";import {sha256,signEd25519,verifyEd25519} from "../packages/provenance/src/signing.mjs";
const {privateKey,publicKey}=generateKeyPairSync("ed25519",{privateKeyEncoding:{type:"pkcs8",format:"pem"},publicKeyEncoding:{type:"spki",format:"pem"}});
const artifact={kind:"Skill",name:"security-review",version:"1.0.0"};
test("artifact digest is deterministic",()=>assert.equal(sha256(artifact),sha256(artifact)));
test("Ed25519 signatures verify",()=>{const s=signEd25519(artifact,privateKey);assert.equal(verifyEd25519(artifact,s,publicKey),true);assert.equal(verifyEd25519({...artifact,version:"2.0.0"},s,publicKey),false);});
