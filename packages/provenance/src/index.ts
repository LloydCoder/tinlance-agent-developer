export interface ProvenanceMaterial{readonly uri:string;readonly digest:string;}
export interface ProvenanceSubject{readonly name:string;readonly digest:{readonly sha256:string;}}
export interface SlsaBuildDefinition{readonly buildType:string;readonly externalParameters:Readonly<Record<string,unknown>>;readonly internalParameters:Readonly<Record<string,unknown>>;readonly resolvedDependencies:readonly ProvenanceMaterial[];}
export interface SlsaRunDetails{readonly builder:{readonly id:string};readonly metadata:{readonly invocationId:string;readonly startedOn:string;readonly finishedOn:string;};}
export interface ProvenanceRecord{readonly type:"https://in-toto.io/Statement/v1";readonly predicateType:"https://slsa.dev/provenance/v1";readonly subject:readonly ProvenanceSubject[];readonly predicate:{readonly buildDefinition:SlsaBuildDefinition;readonly runDetails:SlsaRunDetails;};}
export interface SignatureEnvelope{readonly algorithm:"Ed25519";readonly keyId:string;readonly payloadDigest:string;readonly signature:string;}
export const SLSA_PROVENANCE_V1="https://slsa.dev/provenance/v1";
export function validateProvenance(record:ProvenanceRecord):readonly string[]{
 const e:string[]=[];
 if(record.type!=="https://in-toto.io/Statement/v1")e.push("invalid in-toto statement type");
 if(record.predicateType!==SLSA_PROVENANCE_V1)e.push("invalid SLSA predicate type");
 if(record.subject.length===0)e.push("at least one provenance subject is required");
 for(const subject of record.subject)if(!subject.name||!/^([a-f0-9]{64})$/.test(subject.digest.sha256))e.push("invalid subject SHA-256 digest");
 if(!record.predicate.buildDefinition.buildType)e.push("build type is required");
 if(!record.predicate.runDetails.builder.id)e.push("builder identity is required");
 if(!record.predicate.runDetails.metadata.invocationId)e.push("invocation ID is required");
 return Object.freeze(e);
}
