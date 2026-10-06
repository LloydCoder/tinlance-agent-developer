export type IntegrationLayer="TADL"|"AGENT_OS"|"AGENT_PLATFORM"|"DOMAIN_PRODUCT";
export type AuthorityOwner="AGENT_PLATFORM"|"DOMAIN_PRODUCT";
export interface IntegrationContract{readonly consumer:string;readonly layer:IntegrationLayer;readonly tadlVersion:string;readonly requiredPlatformContract:string;readonly authorityOwner:AuthorityOwner;}
export const ecosystemConsumers=Object.freeze(["FDSE","FDSE Toolkit","BugFlow","TwinGuard","AI Shield","ThreatFade","ReconOS","TADS","FAS","Hezqara","FadeReach"]);
const semver=/^\d+\.\d+\.\d+$/;
export function validateIntegration(c:IntegrationContract):IntegrationContract{
 if(!ecosystemConsumers.includes(c.consumer)&&!["Agent OS","Agent Platform SDK","Agent Platform"].includes(c.consumer))throw new Error("unknown ecosystem consumer");
 if(!semver.test(c.tadlVersion))throw new Error("invalid TADL version");
 if(!c.requiredPlatformContract.trim())throw new Error("required Platform contract is mandatory");
 if((c.layer==="TADL"||c.layer==="AGENT_OS"||c.layer==="AGENT_PLATFORM")&&c.authorityOwner!=="AGENT_PLATFORM")throw new Error("non-domain integrations cannot own authority");
 if(c.layer==="DOMAIN_PRODUCT"&&c.authorityOwner!=="AGENT_PLATFORM"&&c.authorityOwner!=="DOMAIN_PRODUCT")throw new Error("invalid domain authority owner");
 return Object.freeze({...c});
}
export function validateEcosystemMatrix(contracts:readonly IntegrationContract[]):readonly string[]{
 const errors:string[]=[];const seen=new Set<string>();
 for(const contract of contracts){const key=contract.consumer+"@"+contract.tadlVersion;if(seen.has(key))errors.push("duplicate integration contract: "+key);seen.add(key);try{validateIntegration(contract);}catch(error){errors.push(contract.consumer+": "+(error instanceof Error?error.message:String(error)));}}
 for(const consumer of ecosystemConsumers)if(!contracts.some(c=>c.consumer===consumer))errors.push("missing ecosystem contract: "+consumer);
 return Object.freeze(errors);
}
