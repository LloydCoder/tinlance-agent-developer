export interface CanonicalAgent{readonly name:string;readonly version:string;readonly skills:readonly string[];readonly capabilities:readonly string[];readonly model?:string;}
export interface HarnessArtifact{readonly harness:string;readonly version:string;readonly trust:"untrusted";readonly payload:Readonly<Record<string,unknown>>;}
export interface HarnessAdapter{readonly name:string;readonly version:string;compile(agent:CanonicalAgent):HarnessArtifact;}
const safeName=/^[a-z][a-z0-9.-]{2,127}$/;
export function createAdapter(name:string,version:string,compilePayload:(agent:CanonicalAgent)=>Record<string,unknown>):HarnessAdapter{if(!safeName.test(name))throw new Error("invalid harness name");return Object.freeze({name,version,compile(agent:CanonicalAgent){const payload=compilePayload({name:agent.name,version:agent.version,skills:[...agent.skills],capabilities:[...agent.capabilities],model:agent.model});return Object.freeze({harness:name,version,trust:"untrusted" as const,payload:Object.freeze(payload)});}});}
export function assertUntrusted(artifact:HarnessArtifact){if(artifact.trust!=="untrusted")throw new Error("harness trust must remain untrusted");return artifact;}
