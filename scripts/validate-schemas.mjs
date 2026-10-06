import fs from "node:fs";
import path from "node:path";
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?walk(p):[p]})}
const files=walk("schemas").filter(f=>f.endsWith(".schema.json"));
for(const file of files){
  const s=JSON.parse(fs.readFileSync(file,"utf8"));
  if(s.$schema!=="https://json-schema.org/draft/2020-12/schema") throw new Error(`${file}: wrong dialect`);
  if(!s.$id||!s.title) throw new Error(`${file}: missing $id/title`);
}
console.log(`Schema metadata OK: ${files.length} schemas.`);
