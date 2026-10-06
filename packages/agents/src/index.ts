export type AgentState="DRAFT"|"VALIDATED"|"PUBLISHED"|"RETIRED";
export type RiskClass="R0"|"R1"|"R2"|"R3"|"R4"|"R5";
export interface AgentProfile{readonly name:string;readonly version:string;readonly purpose:string;readonly skills:readonly string[];readonly capabilities:readonly string[];readonly model?:string;readonly maxRiskClass:RiskClass;}
export interface PublicationEvidence{readonly artifactDigest:string;readonly evaluationReceiptId:string;readonly evaluationPassed:boolean;readonly provenanceDigest:string;readonly signature:string;readonly publishedAt:string;}
const next:Record<AgentState,readonly AgentState[]>={DRAFT:["VALIDATED"],VALIDATED:["PUBLISHED","DRAFT"],PUBLISHED:["RETIRED"],RETIRED:[]};
const risk=new Set(["R0","R1","R2","R3","R4","R5"]);
const semver=/^\d+\.\d+\.\d+$/;
const name=/^[a-z][a-z0-9.-]{2,127}$/;
export class AgentLifecycle{
 private stateValue:AgentState="DRAFT";
 private publicationValue:PublicationEvidence|undefined;
 constructor(readonly profile:AgentProfile){const errors=validateAgent(profile);if(errors.length)throw new Error(errors.join("; "));this.profile=Object.freeze({...profile,skills:Object.freeze([...profile.skills]),capabilities:Object.freeze([...profile.capabilities]));}
 get state(){return this.stateValue;}
 get publication(){return this.publicationValue;}
 transition(to:AgentState,evidence?:PublicationEvidence){
  if(!next[this.stateValue].includes(to))throw new Error("invalid agent lifecycle transition");
  if(to==="PUBLISHED"){if(!evidence)throw new Error("publication evidence is required");if(!evidence.evaluationPassed)throw new Error("agent cannot publish without a passing evaluation");if(!/^sha256:[a-f0-9]{64}$/.test(evidence.artifactDigest))throw new Error("invalid artifact digest");if(!/^sha256:[a-f0-9]{64}$/.test(evidence.provenanceDigest))throw new Error("invalid provenance digest");if(!evidence.signature.trim())throw new Error("publication signature is required");this.publicationValue=Object.freeze({...evidence});}
  this.stateValue=to;return this.stateValue;
 }
 canExecute(){return this.stateValue==="PUBLISHED"&&Boolean(this.publicationValue?.evaluationPassed);}
}
export function validateAgent(profile:AgentProfile):readonly string[]{
 const e:string[]=[];
 if(!name.test(profile.name))e.push("agent name is invalid");
 if(!semver.test(profile.version))e.push("agent version is invalid");
 if(!profile.purpose.trim())e.push("agent purpose is required");
 if(profile.skills.length===0)e.push("at least one skill is required");
 if(profile.capabilities.length===0)e.push("at least one capability is required");
 if(!risk.has(profile.maxRiskClass))e.push("invalid maximum risk class");
 return Object.freeze(e);
}
