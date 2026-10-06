export interface SkillManifest{readonly name:string;readonly version:string;readonly purpose:string;readonly dependencies:readonly string[];readonly requiredCapabilities:readonly string[];readonly evaluationSuite?:string;}
export interface SkillPackage{readonly manifest:SkillManifest;readonly files:Readonly<Record<string,string>>;}
export interface SkillDiagnostic{readonly code:string;readonly message:string;}
const requiredFiles=["skill.yaml","SKILL.md"];
const allowedRoots=["instructions/","references/","prompts/","tools/","evaluations/","fixtures/"];
const maxFileBytes=1024*1024;
const validName=(name:string)=>/^[a-z][a-z0-9.-]{2,127}$/.test(name);
const validVersion=(v:string)=>/^\d+\.\d+\.\d+$/.test(v);
function normalizedPath(input:string):string{
 if(!input||input.includes("\\")||input.startsWith("/")||input.includes("\0"))throw new Error("invalid skill file path");
 const parts=input.split("/");
 if(parts.some(p=>!p||p==="."||p===".."||p.includes("\u0000")))throw new Error("invalid skill file path");
 return parts.join("/");
}
function allowedFile(input:string):boolean{return requiredFiles.includes(input)||input==="CHANGELOG.md"||allowedRoots.some(root=>input.startsWith(root));}
export function validateSkill(pkg:SkillPackage):readonly SkillDiagnostic[]{
 const e:SkillDiagnostic[]=[]; const m=pkg.manifest;
 if(!validName(m.name))e.push({code:"NAME_INVALID",message:"skill name is invalid"});
 if(!validVersion(m.version))e.push({code:"VERSION_INVALID",message:"skill version is invalid"});
 if(typeof m.purpose!=="string"||!m.purpose.trim())e.push({code:"PURPOSE_EMPTY",message:"skill purpose is required"});
 if(!Array.isArray(m.dependencies))e.push({code:"DEPENDENCIES_INVALID",message:"dependencies must be an array"});
 if(!Array.isArray(m.requiredCapabilities))e.push({code:"CAPABILITIES_INVALID",message:"requiredCapabilities must be an array"});
 const seen=new Set<string>();
 for(const f of Object.keys(pkg.files)){
  try{const normalized=normalizedPath(f);if(normalized!==f)e.push({code:"PATH_NOT_NORMALIZED",message:"file path must be normalized: "+f});if(!allowedFile(normalized))e.push({code:"FILE_NOT_ALLOWED",message:"file path is outside the skill package layout: "+f});if(seen.has(normalized))e.push({code:"DUPLICATE_PATH",message:"duplicate normalized file path: "+f});seen.add(normalized);if(Buffer.byteLength(pkg.files[f],"utf8")>maxFileBytes)e.push({code:"FILE_TOO_LARGE",message:"file exceeds 1 MiB: "+f});}catch(error){e.push({code:"PATH_INVALID",message:error instanceof Error?error.message:"invalid file path"});}
 }
 for(const f of requiredFiles)if(!(f in pkg.files))e.push({code:"FILE_MISSING",message:"required file missing: "+f});
 for(const d of m.dependencies??[]){if(d===m.name)e.push({code:"SELF_DEPENDENCY",message:"skill cannot depend on itself"});if(typeof d!=="string"||!validName(d))e.push({code:"DEPENDENCY_INVALID",message:"invalid dependency name: "+String(d)});}
 for(const c of m.requiredCapabilities??[])if(typeof c!=="string"||!c.trim())e.push({code:"CAPABILITY_INVALID",message:"required capability must be non-empty"});
 return Object.freeze(e);
}
export function assertSkill(pkg:SkillPackage):SkillPackage{
 const errors=validateSkill(pkg); if(errors.length)throw new Error(errors.map(x=>x.code+": "+x.message).join("; "));
 const manifest=Object.freeze({...pkg.manifest,dependencies:Object.freeze([...pkg.manifest.dependencies]),requiredCapabilities:Object.freeze([...pkg.manifest.requiredCapabilities])});
 const files=Object.freeze({...pkg.files});
 return Object.freeze({...pkg,manifest,files});
}
export function dependencyOrder(skills:readonly SkillPackage[]):readonly string[]{
 const ordered=[...skills].sort((a,b)=>a.manifest.name.localeCompare(b.manifest.name));
 const byName=new Map(ordered.map(s=>[s.manifest.name,s])); const state=new Map<string,number>(); const out:string[]=[];
 function visit(name:string){const s=state.get(name)||0;if(s===1)throw new Error("skill dependency cycle");if(s===2)return;state.set(name,1);const item=byName.get(name);if(!item)throw new Error("missing skill dependency: "+name);for(const d of [...item.manifest.dependencies].sort())visit(d);state.set(name,2);out.push(name);}
 for(const s of ordered)visit(s.manifest.name); return Object.freeze(out);
}
