import {sha256} from "../../provenance/src/signing.mjs";
import type {EvaluationReceipt} from "./index.js";
export interface AuthorityState{readonly identity:Readonly<Record<string,unknown>>;readonly authorizations:Readonly<Record<string,unknown>>;readonly policies:Readonly<Record<string,unknown>>;readonly approvals:Readonly<Record<string,unknown>>;}
export interface LearningProposal{readonly id:string;readonly target:string;readonly behaviorDelta:Readonly<Record<string,unknown>>;readonly baselineAuthorityDigest:string;readonly evaluationReceipt:EvaluationReceipt;}
export function authorityDigest(state:AuthorityState){return sha256(state);}
export function acceptLearningProposal(p:LearningProposal,currentAuthority:AuthorityState){
 if(!p.id.trim()||!p.target.trim())throw new Error("learning proposal identity is required");
 if(p.baselineAuthorityDigest!==authorityDigest(currentAuthority))throw new Error("learning proposal authority baseline does not match current authority");
 if(!p.evaluationReceipt.passed)throw new Error("learning proposal has not passed evaluation");
 return Object.freeze({...p,behaviorDelta:Object.freeze({...p.behaviorDelta})});
}
