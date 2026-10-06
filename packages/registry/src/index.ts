import {sha256} from "../../provenance/src/signing.mjs";

export type TrustLevel = "UNKNOWN"|"UNVERIFIED"|"VERIFIED"|"TINLANCE_SIGNED"|"ENTERPRISE_APPROVED"|"SYSTEM";
export interface RegistryArtifact{readonly kind:string;readonly name:string;readonly version:string;readonly digest:string;readonly trust:TrustLevel;readonly payload:unknown;readonly publishedAt:string;readonly revoked?:boolean;readonly deprecated?:boolean;}
export type RegistryEvent =
  | {readonly type:"PUBLISHED";readonly sequence:number;readonly artifact:RegistryArtifact;readonly at:string}
  | {readonly type:"REVOKED";readonly sequence:number;readonly kind:string;readonly name:string;readonly version:string;readonly at:string}
  | {readonly type:"DEPRECATED";readonly sequence:number;readonly kind:string;readonly name:string;readonly version:string;readonly at:string};
export class RegistryError extends Error{}
const freezeArtifact=(artifact:RegistryArtifact):RegistryArtifact=>Object.freeze({...artifact});
export class ImmutableRegistry{
 private readonly records=new Map<string,RegistryArtifact>();
 private readonly eventsLog:RegistryEvent[]=[];
 private key(kind:string,name:string,version:string){return kind+"/"+name+"@"+version;}
 publish(artifact:RegistryArtifact):RegistryArtifact{
  const k=this.key(artifact.kind,artifact.name,artifact.version);
  if(this.records.has(k))throw new RegistryError("artifact version already exists");
  if(!/^sha256:[a-f0-9]{64}$/.test(artifact.digest))throw new RegistryError("artifact digest must be sha256:<64 lowercase hex>");\n  if(artifact.digest!==registryDigest(artifact.payload))throw new RegistryError("artifact digest does not match payload");
  const frozen=freezeArtifact(artifact); this.records.set(k,frozen);
  this.eventsLog.push(Object.freeze({type:"PUBLISHED",sequence:this.eventsLog.length+1,artifact:frozen,at:artifact.publishedAt}));
  return frozen;
 }
 get(kind:string,name:string,version:string){return this.records.get(this.key(kind,name,version));}
 list(kind?:string):readonly RegistryArtifact[]{return Object.freeze([...this.records.values()].filter(x=>!kind||x.kind===kind));}
 revoke(kind:string,name:string,version:string):RegistryArtifact{
  const k=this.key(kind,name,version),current=this.get(kind,name,version);
  if(!current)throw new RegistryError("artifact not found");
  if(current.revoked)return current;
  const next=freezeArtifact({...current,revoked:true}); this.records.set(k,next);
  this.eventsLog.push(Object.freeze({type:"REVOKED",sequence:this.eventsLog.length+1,kind,name,version,at:new Date().toISOString()}));
  return next;
 }
 deprecate(kind:string,name:string,version:string):RegistryArtifact{
  const k=this.key(kind,name,version),current=this.get(kind,name,version);
  if(!current)throw new RegistryError("artifact not found");
  if(current.deprecated)return current;
  const next=freezeArtifact({...current,deprecated:true}); this.records.set(k,next);
  this.eventsLog.push(Object.freeze({type:"DEPRECATED",sequence:this.eventsLog.length+1,kind,name,version,at:new Date().toISOString()}));
  return next;
 }
 resolve(kind:string,name:string,version:string):RegistryArtifact{
  const item=this.get(kind,name,version); if(!item)throw new RegistryError("artifact not found");
  if(item.revoked)throw new RegistryError("artifact is revoked"); return item;
 }
 events():readonly RegistryEvent[]{return Object.freeze(this.eventsLog.map(event=>Object.freeze({...event})));}
}
