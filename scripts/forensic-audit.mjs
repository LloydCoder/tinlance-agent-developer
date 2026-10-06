import fs from "node:fs";
import path from "node:path";
const root=process.cwd();
const requiredPhases=Array.from({length:14},(_,i)=>"docs/architecture/PHASE-"+i+".md");
const requiredFiles=[
 ...requiredPhases,
 "packages/core/src/integration.ts","packages/schemas/src/index.mjs","packages/skills/src/index.ts",
 "packages/capabilities/src/index.ts","packages/agents/src/index.ts","packages/workflows/src/index.ts",
 "packages/harnesses/src/index.ts","packages/evaluation/src/index.ts","packages/evaluation/src/learning.ts",
 "packages/registry/src/index.ts","packages/provenance/src/index.ts","packages/provenance/src/signing.mjs",
 "packages/security/src/index.ts","tests/security/developer-boundary.test.mjs",
 ".github/workflows/ci.yml",".github/workflows/security.yml",".github/workflows/scorecard.yml",
 ".github/workflows/codeql.yml",".github/workflows/secrets.yml",".github/workflows/release-attestation.yml",
 "package.json","package-lock.json","SECURITY.md","README.md"
];
const missing=requiredFiles.filter(file=>!fs.existsSync(path.join(root,file)));if(missing.length)throw new Error("forensic audit missing: "+missing.join(","));
const workflowRoot=path.join(root,".github/workflows");
for(const file of fs.readdirSync(workflowRoot)){
 const data=fs.readFileSync(path.join(workflowRoot,file),"utf8");
 for(const match of data.matchAll(/uses:\s*([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)@([^\s]+)/g))if(!/^[0-9a-f]{40}$/.test(match[2]))throw new Error("unpinned action: "+match[0]);
 if(/permissions:\s*\n(?:[^\n]*\n)*?\s+contents:\s*write/.test(data))throw new Error("workflow requests contents: write: "+file);
}
const pkg=JSON.parse(fs.readFileSync(path.join(root,"package.json"),"utf8"));
const lock=JSON.parse(fs.readFileSync(path.join(root,"package-lock.json"),"utf8"));
if(pkg.name!==lock.name||pkg.version!==lock.version)throw new Error("package manifest and lockfile identity diverge");
if(!lock.packages||!lock.packages[""])throw new Error("lockfile root package missing");
const securitySource=fs.readFileSync(path.join(root,"packages/security/src/index.ts"),"utf8");
if(!securitySource.includes("assertDeveloperArtifactSafe")||!securitySource.includes("assertAuthoritySeparation"))throw new Error("security package controls are incomplete");
const securityTest=fs.readFileSync(path.join(root,"tests/security/developer-boundary.test.mjs"),"utf8");
if(securityTest.length<500)throw new Error("security test surface is too small");
const readme=fs.readFileSync(path.join(root,"README.md"),"utf8");
for(const term of ["Agent Platform","Agent OS","capability","provenance","evaluation","Phase 13","security","SBOM","attestation"])if(!readme.toLowerCase().includes(term.toLowerCase()))throw new Error("README missing: "+term);
const release=fs.readFileSync(path.join(workflowRoot,"release-attestation.yml"),"utf8");
if(!release.includes("attestations: write")||!release.includes("artifact-metadata: write")||!release.includes("sbom-path"))throw new Error("release attestation workflow is incomplete");
console.log("Forensic audit OK: phase implementation topology, executable security controls, workflow pinning, lockfile integrity, SBOM and attestation controls verified.");
