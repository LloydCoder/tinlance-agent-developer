import fs from "node:fs";
import path from "node:path";
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?walk(p):[p]})}
const files=walk(".").filter(f=>/\.(js|mjs|ts|json|md|yaml|yml)$/.test(f)&&!f.includes("node_modules/"));
for(const file of files){
  const data=fs.readFileSync(file,"utf8");
  if(data.includes("\r\n")) throw new Error(`${file}: CRLF line endings are not allowed`);
  if(/bypass.{0,40}authorization/i.test(data)) throw new Error(`${file}: suspicious authorization-bypass marker`);
}
console.log(`Lint OK: ${files.length} text artifacts scanned.`);
