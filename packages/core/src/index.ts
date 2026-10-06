export type RiskClass = "R0" | "R1" | "R2" | "R3" | "R4" | "R5";
export type TrustLevel = "UNKNOWN" | "UNVERIFIED" | "VERIFIED" | "TINLANCE_SIGNED" | "ENTERPRISE_APPROVED" | "SYSTEM";
export interface ArtifactMetadata { readonly name: string; readonly version: string; readonly digest?: string; }
export interface ArtifactRef { readonly kind: string; readonly name: string; readonly version: string; readonly digest?: string; }
export interface CapabilityRequirement { readonly authorizations: readonly string[]; readonly tools: readonly string[]; readonly approvals: readonly string[]; readonly evidence: readonly string[]; }
export interface CapabilityContract { readonly metadata: ArtifactMetadata; readonly risk: RiskClass; readonly requires: CapabilityRequirement; }
