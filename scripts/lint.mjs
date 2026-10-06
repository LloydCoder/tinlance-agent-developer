import fs from "node:fs";
import path from "node:path";
const roots=["docs","schemas","packages","cli","examples","tests",".github","README.md","SECURITY.md","CONTRIBUTING.md","CHANGELOG.md","CODE_OF_CONDUCT.md"];
const files=[];
function add(p){if(!fs.existsSync(p))return;const s=fs.statSync(p);if(s.isDirectory())for(const e of fs.readdirSync(p))add(path.join(p,e));else files.push(p)}
for(const r of roots)add(path.join(process.cwd(),r));
for(const f of files){const b=fs.readFileSync(f);if(b.includes(Buffer.from([13,10])))throw new Error("CRLF: "+f);}
console.log("Lint OK:",files.length,"files");
