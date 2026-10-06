export type TrustLevel="UNKNOWN"|"UNVERIFIED"|"VERIFIED"|"TINLANCE_SIGNED"|"ENTERPRISE_APPROVED"|"SYSTEM";
export interface RegistryArtifact{readonly kind:string;readonly name:string;readonly version:string;readonly digest:string;readonly trust:TrustLevel;readonly payload:unknown;readonly publishedAt:string;readonly revoked?:boolean;readonly deprecated?:boolean;}
export class RegistryError extends Error{}
export class ImmutableRegistry{
 private readonly records=new Map<string,RegistryArtifact>();
 private key(kind:string,name:string,version:string){return kind+"/"+name+"@"+version;}
 publish(artifact:RegistryArtifact):RegistryArtifact{const k=this.key(artifact.kind,artifact.name,artifact.version);if(this.records.has(k))throw new RegistryError("artifact version already exists");const frozen=Object.freeze({...artifact});this.records.set(k,frozen);return frozen;}
 get(kind:string,name:string,version:string):RegistryArtifact|undefined{return this.records.get(this.key(kind,name,version));}
 list(kind?:string):readonly RegistryArtifact[]{return Object.freeze([...this.records.values()].filter(x=>!kind||x.kind===kind));}
 revoke(kind:string,name:string,version:string):RegistryArtifact{const current=this.get(kind,name,version);if(!current)throw new RegistryError("artifact not found");const next=Object.freeze({...current,revoked:true});this.records.set(this.key(kind,name,version),next);return next;}
 deprecate(kind:string,name:string,version:string):RegistryArtifact{const current=this.get(kind,name,version);if(!current)throw new RegistryError("artifact not found");const next=Object.freeze({...current,deprecated:true});this.records.set(this.key(kind,name,version),next);return next;}
 resolve(kind:string,name:string,version:string):RegistryArtifact{const item=this.get(kind,name,version);if(!item)throw new RegistryError("artifact not found");if(item.revoked)throw new RegistryError("artifact is revoked");return item;}
}