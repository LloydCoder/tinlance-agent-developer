#!/usr/bin/env node
import fs from "node:fs";
import {validateArtifact} from "../packages/schemas/src/index.mjs";
const [command,...args]=process.argv.slice(2);
function usage(){console.log("tadl validate <schema-relative-path> <artifact.json>\ntadl help");}
if(!command||command==="help"){usage();process.exit(0);}
if(command==="validate"){const [schema,artifactPath]=args;if(!schema||!artifactPath){usage();process.exit(2);}const artifact=JSON.parse(fs.readFileSync(artifactPath,"utf8"));const result=validateArtifact(schema,artifact);if(!result.valid){for(const e of result.errors)console.error(e.path+": "+e.message);process.exit(1);}console.log("valid");process.exit(0);}
console.error("unknown command");usage();process.exit(2);
