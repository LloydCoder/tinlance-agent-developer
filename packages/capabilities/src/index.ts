export type RiskClass="R0"|"R1"|"R2"|"R3"|"R4"|"R5";
const rank:Record<RiskClass,number>={R0:0,R1:1,R2:2,R3:3,R4:4,R5:5};
export interface CapabilityContract{readonly name:string;readonly version:string;readonly risk:RiskClass;readonly authorizations:readonly string[];readonly tools:readonly string[];readonly approvals:readonly string[];readonly evidence:readonly string[];readonly evaluation:{readonly suite:string;readonly minimumScore:number};}
export interface AuthorizationGrant{readonly capability:string;readonly version:string;readonly tenantId:string;readonly principalId:string;readonly environment:string;readonly resourceScopes:readonly string[];readonly maxRisk:RiskClass;readonly policyDigest:string;readonly expiresAt:string;}
export interface ApprovalGrant{readonly capability:string;readonly version:string;readonly tenantId:string;readonly approvalId:string;readonly expiresAt:string;}
export interface AuthorizationContext{readonly tenantId:string;readonly principalId:string;readonly environment:string;readonly resource:string;readonly policyDigest:string;readonly grants:readonly AuthorizationGrant[];readonly approvals?:readonly ApprovalGrant[];}
export function riskAtMost(actual:RiskClass,maximum:RiskClass){return rank[actual]<=rank[maximum];}
function notExpired(value:string){const time=Date.parse(value);return Number.isFinite(time)&&time>Date.now();}
function scopeMatches(resource:string,scopes:readonly string[]){return scopes.some(scope=>scope==="*"||scope===resource||(scope.endsWith("/*")&&resource.startsWith(scope.slice(0,-1))));}
export function effectiveCapabilities(declared:readonly CapabilityContract[],context:AuthorizationContext):readonly CapabilityContract[]{
 const approvals=new Map((context.approvals??[]).map(a=>[a.capability+"@"+a.version,a]));
 return Object.freeze(declared.filter(cap=>{
  const grant=context.grants.find(g=>g.capability===cap.name&&g.version===cap.version&&g.tenantId===context.tenantId&&g.principalId===context.principalId&&g.environment===context.environment&&g.policyDigest===context.policyDigest&&riskAtMost(cap.risk,g.maxRisk)&&scopeMatches(context.resource,g.resourceScopes)&&notExpired(g.expiresAt));
  if(!grant)return false;
  if(cap.approvals.length===0)return true;
  const approval=approvals.get(cap.name+"@"+cap.version);
  return Boolean(approval&&approval.tenantId===context.tenantId&&notExpired(approval.expiresAt));
 }));
}
export function validateCapability(c:CapabilityContract):readonly string[]{
 const e:string[]=[];
 if(!c.name||!c.version)e.push("identity required");
 if(!/^[a-z][a-z0-9.-]{2,127}$/.test(c.name))e.push("capability name is invalid");
 if(!/^\d+\.\d+\.\d+$/.test(c.version))e.push("capability version is invalid");
 if(c.evaluation.minimumScore<0||c.evaluation.minimumScore>1)e.push("evaluation score must be between 0 and 1");
 if(c.risk==="R0"&&c.tools.some(t=>/(^|[.:_-])(write|delete|merge|deploy|execute)([.:_-]|$)/i.test(t)))e.push("informational capabilities cannot require mutating tools");
 if(rank[c.risk]>=rank.R3&&c.approvals.length===0)e.push("consequential capabilities require an approval declaration");
 if(rank[c.risk]>=rank.R4&&c.evidence.length===0)e.push("privileged capabilities require evidence requirements");
 return Object.freeze(e);
}
export function assertCapability(c:CapabilityContract):CapabilityContract{
 const e=validateCapability(c);if(e.length)throw new Error(e.join("; "));
 return Object.freeze({...c,authorizations:Object.freeze([...c.authorizations]),tools:Object.freeze([...c.tools]),approvals:Object.freeze([...c.approvals]),evidence:Object.freeze([...c.evidence]),evaluation:Object.freeze({...c.evaluation})});
}
