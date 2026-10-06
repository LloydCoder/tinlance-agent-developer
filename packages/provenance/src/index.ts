export interface ProvenanceMaterial{readonly uri:string;readonly digest:string;}
export interface ProvenanceRecord{readonly predicateType:string;readonly subject:{readonly name:string;readonly digest:string};readonly materials:readonly ProvenanceMaterial[];}
export const SLSA_PROVENANCE_V1="https://slsa.dev/provenance/v1";
