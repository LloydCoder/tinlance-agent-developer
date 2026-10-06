import {createHash,createPrivateKey,createPublicKey,sign,verify} from "node:crypto";
export function canonicalJson(value){return JSON.stringify(value,Object.keys(value).sort());}
export function sha256(value){return "sha256:"+createHash("sha256").update(typeof value==="string"?value:canonicalJson(value)).digest("hex");}
export function signEd25519(value,privateKeyPem){const data=Buffer.from(canonicalJson(value));return sign(null,data,createPrivateKey(privateKeyPem)).toString("base64");}
export function verifyEd25519(value,signature,publicKeyPem){const data=Buffer.from(canonicalJson(value));return verify(null,data,createPublicKey(publicKeyPem),Buffer.from(signature,"base64"));}
