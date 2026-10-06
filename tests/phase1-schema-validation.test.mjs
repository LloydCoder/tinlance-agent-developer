import test from "node:test";import assert from "node:assert/strict";import {validateArtifact} from "../dist/packages/schemas/src/index.js";
const valid={apiVersion:"tadl.tinlance.com/v1",kind:"Capability",metadata:{name:"repository.security.assess",version:"1.0.0"},risk:{class:"R1"},spec:{inputs:{},outputs:{},requires:{authorizations:["repository.read"],tools:["repository.inspect"],approvals:[],evidence:[]}}};
test("valid capability passes canonical schema",()=>assert.equal(validateArtifact("capability/v1/capability.schema.json",valid).valid,true));
test("invalid risk fails canonical schema",()=>assert.equal(validateArtifact("capability/v1/capability.schema.json",{...valid,risk:{class:"R9"}}).valid,false));
test("unknown properties are rejected",()=>assert.equal(validateArtifact("capability/v1/capability.schema.json",{...valid,unexpected:true}).valid,false));
