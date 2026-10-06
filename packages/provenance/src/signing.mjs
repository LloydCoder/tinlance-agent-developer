import {createHash,createPrivateKey,createPublicKey,sign,verify} from "node:crypto";
function canonical(value){
 if(value===null||typeof value==="boolean"||typeof value==="string")return JSON.stringify(value);
 if(typeof value==="number"){if(!Number.isFinite(value))throw new TypeError("non-finite numbers cannot be canonicalized");return JSON.stringify(value);}
 if(Array.isArray(value))return "["+value.map(canonical).join(",")+"]";
 if(typeof value==="object")return "{"+Object.keys(value).sort().map(key=>JSON.stringify(key)+":"+canonical(value[key])).join(",")+"}";
 throw new TypeError("unsupported value in canonical JSON");
}
export function canonicalJson(value){return canonical(value);}
export function sha256(value){return "sha256:"+createHash("sha256").update(typeof value==="string"?value:canonical(value)).digest("hex");}
export function signEd25519(value,privateKeyPem){return sign(null,Buffer.from(canonical(value)),createPrivateKey(privateKeyPem)).toString("base64");}
export function verifyEd25519(value,signature,publicKeyPem){return verify(null,Buffer.from(canonical(value)),createPublicKey(publicKeyPem),Buffer.from(signature,"base64"));}
export function createSignatureEnvelope(value,privateKeyPem,keyId){if(!keyId||!keyId.trim())throw new Error("keyId is required");return Object.freeze({algorithm:"Ed25519",keyId,payloadDigest:sha256(value),signature:signEd25519(value,privateKeyPem)});}
export function verifySignatureEnvelope(value,envelope,publicKeyPem){return envelope.algorithm==="Ed25519"&&envelope.payloadDigest===sha256(value)&&verifyEd25519(value,envelope.signature,publicKeyPem);}
