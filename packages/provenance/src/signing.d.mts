export function canonicalJson(value: unknown): string;
export function sha256(value: unknown): string;
export function signEd25519(value: unknown, privateKeyPem: string): string;
export function verifyEd25519(value: unknown, signature: string, publicKeyPem: string): boolean;
export function createSignatureEnvelope(value: unknown, privateKeyPem: string, keyId: string): {readonly algorithm:"Ed25519";readonly keyId:string;readonly payloadDigest:string;readonly signature:string};
export function verifySignatureEnvelope(value: unknown, envelope: {readonly algorithm:string;readonly keyId:string;readonly payloadDigest:string;readonly signature:string}, publicKeyPem: string): boolean;
