#!/usr/bin/env node
import fs from "node:fs";
import {validateArtifact} from "../packages/schemas/src/index.mjs";
import {validateWorkflow,compileWorkflow} from "../dist/packages/workflows/src/index.js";
import {validateAgent} from "../dist/packages/agents/src/index.js";
import {validateCapability} from "../dist/packages/capabilities/src/index.js";

function usage(){
 console.log([
  "tadl help",
  "tadl validate <schema-relative-path> <artifact.json>",
  "tadl capability inspect <artifact.json>",
  "tadl workflow validate <workflow.json>",
  "tadl agent validate <agent.json>",
  "tadl skill validate <skill.json>"
 ].join("\n"));
}
function readJson(file){try{return JSON.parse(fs.readFileSync(file,"utf8"));}catch(error){console.error("cannot read JSON: "+(error instanceof Error?error.message:String(error)));process.exit(2);}}
function printErrors(errors){for(const error of errors)console.error(typeof error==="string"?error:(error.path||"<root>")+": "+error.message);}
const [command,...args]=process.argv.slice(2);
if(!command||command==="help"){usage();process.exit(0);}
if(command==="validate"){
 const [schema,file]=args;if(!schema||!file){usage();process.exit(2);}
 const result=validateArtifact(schema,readJson(file));if(!result.valid){printErrors(result.errors);process.exit(1);}console.log(JSON.stringify({valid:true,schema},null,2));process.exit(0);
}
if(command==="capability"&&args[0]==="inspect"){
 const artifact=readJson(args[1]);const metadata=artifact.metadata??artifact;const spec=artifact.spec??{};
 const risk=artifact.risk?.class??"UNKNOWN";console.log(JSON.stringify({name:metadata.name,version:metadata.version,risk,authorizations:spec.requires?.authorizations??[],tools:spec.requires?.tools??[],approvals:spec.requires?.approvals??[],evidence:spec.requires?.evidence??[]},null,2));process.exit(0);
}
if(command==="workflow"&&args[0]==="validate"){
 const artifact=readJson(args[1]);const spec=artifact.spec??artifact;const workflow={name:artifact.metadata?.name??artifact.name,version:artifact.metadata?.version??artifact.version,steps:spec.steps??[]};const errors=validateWorkflow(workflow);if(errors.length){printErrors(errors);process.exit(1);}const compiled=compileWorkflow(workflow);console.log(JSON.stringify({valid:true,order:compiled.order},null,2));process.exit(0);
}
if(command==="agent"&&args[0]==="validate"){
 const artifact=readJson(args[1]);const spec=artifact.spec??artifact;const profile={name:artifact.metadata?.name??artifact.name,version:artifact.metadata?.version??artifact.version,purpose:spec.purpose??"agent",skills:spec.skills??[],capabilities:spec.capabilities?.allow??spec.capabilities??[],maxRiskClass:spec.maxRiskClass??"R0"};const errors=validateAgent(profile);if(errors.length){printErrors(errors);process.exit(1);}console.log(JSON.stringify({valid:true,name:profile.name,version:profile.version},null,2));process.exit(0);
}
if(command==="skill"&&args[0]==="validate"){
 const artifact=readJson(args[1]);const result=validateArtifact("skill/v1/skill.schema.json",artifact);if(!result.valid){printErrors(result.errors);process.exit(1);}console.log(JSON.stringify({valid:true,name:artifact.metadata.name,version:artifact.metadata.version},null,2));process.exit(0);
}
console.error("unknown command or arguments");usage();process.exit(2);
