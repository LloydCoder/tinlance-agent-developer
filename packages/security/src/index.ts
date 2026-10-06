export type SecuritySeverity="LOW"|"MEDIUM"|"HIGH"|"CRITICAL";
export interface SecurityFinding{readonly code:string;readonly severity:SecuritySeverity;readonly path:string;readonly message:string;}
const forbiddenAuthorityKeys=new Set(["authorize","authorization","permissions","grant","privilege","secret","token","credential"]);
const secretPatterns=[
 /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/,
 /\bgh[pousr]_[A-Za-z0-9_]{20,}\b/,
 /\bAKIA[0-9A-Z]{16}\b/,
 /\bBearer\s+[A-Za-z0-9._-]{20,}/i
];
function walk(value:unknown,path:string,out:SecurityFinding[]){
 if(value===null||typeof value!=="object"){if(typeof value==="string")for(const pattern of secretPatterns)if(pattern.test(value))out.push({code:"SECRET_LIKE_VALUE",severity:"CRITICAL",path,message:"secret-like material detected in developer artifact"});return;}
 if(Array.isArray(value)){value.forEach((item,index)=>walk(item,path+"/"+index,out));return;}
 for(const [key,child] of Object.entries(value)){
  if(forbiddenAuthorityKeys.has(key.toLowerCase()))out.push({code:"AUTHORITY_FIELD",severity:"CRITICAL",path:path+"/"+key,message:"developer artifacts cannot define execution authority"});
  walk(child,path+"/"+key.replace(/~/g,"~0").replace(/\//g,"~1"),out);
 }
}
export function scanDeveloperArtifact(value:unknown):readonly SecurityFinding[]{const findings:SecurityFinding[]=[];walk(value,"",findings);return Object.freeze(findings);}
export function assertDeveloperArtifactSafe(value:unknown){const findings=scanDeveloperArtifact(value);if(findings.length)throw new Error(findings.map(f=>f.code+"@"+f.path).join("; "));return value;}
export function assertAuthoritySeparation(declared:readonly string[],authorized:readonly string[]):readonly string[]{const allowed=new Set(authorized);return Object.freeze(declared.filter(cap=>allowed.has(cap)));}
