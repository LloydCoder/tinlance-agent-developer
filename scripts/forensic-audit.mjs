import fs from "node:fs";import path from "node:path";
const root=process.cwd();const requiredPhases=Array.from({length:14},(_,i)=>"docs/architecture/PHASE-"+i+".md");
const requiredDirs=["packages/core/src","packages/schemas/src","packages/skills/src","packages/capabilities/src","packages/agents/src","packages/workflows/src","packages/harnesses/src","packages/evaluation/src","packages/registry/src","packages/provenance/src","packages/security"];
const missing=[...requiredPhases,...requiredDirs].filter(p=>!fs.existsSync(path.join(root,p)));if(missing.length)throw new Error("forensic audit missing: "+missing.join(","));
for(const file of fs.readdirSync(path.join(root,".github/workflows"))){const data=fs.readFileSync(path.join(root,".github/workflows",file),"utf8");for(const match of data.matchAll(/uses:\s*([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)@([^\s]+)/g)){if(!/^[0-9a-f]{40}$/.test(match[2]))throw new Error("unpinned action: "+match[0]);}}
const readme=fs.readFileSync(path.join(root,"README.md"),"utf8");for(const term of ["Agent Platform","Agent OS","capability","provenance","evaluation","Phase 13"])if(!readme.includes(term))throw new Error("README missing: "+term);
console.log("Forensic audit OK: phase docs, package topology, workflow pinning, and README coverage.");
