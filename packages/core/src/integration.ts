export type IntegrationLayer="TADL"|"AGENT_OS"|"AGENT_PLATFORM"|"DOMAIN_PRODUCT";
export interface IntegrationContract{readonly consumer:string;readonly layer:IntegrationLayer;readonly tadlVersion:string;readonly requiredPlatformContract:string;readonly authorityOwner:"AGENT_PLATFORM"|"DOMAIN_PRODUCT";}
export const ecosystemConsumers=Object.freeze(["FDSE","FDSE Toolkit","BugFlow","TwinGuard","AI Shield","ThreatFade","ReconOS","TADS","FAS","Hezqara","FadeReach"]);
export function validateIntegration(c:IntegrationContract){if(c.layer==="TADL"&&c.authorityOwner!=="AGENT_PLATFORM")throw new Error("TADL integration cannot own authority");return Object.freeze({...c});}
