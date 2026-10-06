export interface CanonicalAgent{readonly name:string;readonly version:string;readonly skills:readonly string[];readonly capabilities:readonly string[];readonly model?:string;}
export interface HarnessArtifact{readonly harness:string;readonly version:string;readonly trust:"untrusted";readonly payload:Readonly<Record<string,unknown>>;}
export interface HarnessAdapter{readonly name:string;readonly version:string;readonly trust:"untrusted";readonly features:readonly string[];compile(agent:CanonicalAgent):HarnessArtifact;}
const safeName=/^[a-z][a-z0-9.-]{2,127}$/; const safeVersion=/^\d+\.\d+\.\d+$/;
function deepFreeze<T>(value:T):T{if(value&&typeof value==="object"&&!Object.isFrozen(value)){Object.freeze(value);for(const child of Object.values(value as Record<string,unknown>))deepFreeze(child);}return value;}
function canonicalInput(agent:CanonicalAgent):CanonicalAgent{return Object.freeze({name:agent.name,version:agent.version,skills:Object.freeze([...agent.skills]),capabilities:Object.freeze([...agent.capabilities]),model:agent.model});}
function validAgent(agent:CanonicalAgent){return safeName.test(agent.name)&&safeVersion.test(agent.version)&&agent.skills.every(s=>typeof s==="string")&&agent.capabilities.every(c=>typeof c==="string");}
export function createAdapter(name:string,version:string,compilePayload:(agent:CanonicalAgent)=>Record<string,unknown>,features:readonly string[]=[]):HarnessAdapter{
 if(!safeName.test(name))throw new Error("invalid harness name"); if(!safeVersion.test(version))throw new Error("invalid harness version");
 const adapter=Object.freeze({name,version,trust:"untrusted" as const,features:Object.freeze([...features]),compile(agent:CanonicalAgent){
  if(!validAgent(agent))throw new Error("invalid canonical agent");
  const input=canonicalInput(agent); const raw=compilePayload(input);
  if(!raw||typeof raw!=="object"||Array.isArray(raw))throw new Error("harness payload must be a plain object");
  const payload=Object.freeze({...raw});
  return Object.freeze({harness:name,version,trust:"untrusted" as const,payload});
 }});
 return adapter;
}
export function assertUntrusted(artifact:HarnessArtifact){if(artifact.trust!=="untrusted")throw new Error("harness trust must remain untrusted");return artifact;}
export function sanitizeHarnessArtifact(artifact:HarnessArtifact):HarnessArtifact{if(artifact.trust!=="untrusted")throw new Error("harness artifact cannot become trusted");return Object.freeze({...artifact,payload:deepFreeze({...artifact.payload})});}
