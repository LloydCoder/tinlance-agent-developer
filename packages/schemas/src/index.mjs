import fs from "node:fs";
import path from "node:path";
const schemaRoot=path.resolve(process.cwd(),"schemas");
function typeOk(value,expected){if(expected==="object")return typeof value==="object"&&value!==null&&!Array.isArray(value);if(expected==="array")return Array.isArray(value);if(expected==="string")return typeof value==="string";if(expected==="number")return typeof value==="number"&&Number.isFinite(value);if(expected==="integer")return typeof value==="number"&&Number.isInteger(value);if(expected==="boolean")return typeof value==="boolean";if(expected==="null")return value===null;return true;}
function walk(schema,value,at,errors){
 if(schema.const!==undefined&&JSON.stringify(value)!==JSON.stringify(schema.const))errors.push({path:at,message:"must equal the declared constant"});
 if(schema.enum&&!schema.enum.some(x=>JSON.stringify(x)===JSON.stringify(value)))errors.push({path:at,message:"must be one of the declared enum values"});
 if(schema.type&&!typeOk(value,schema.type)){errors.push({path:at,message:"has the wrong type"});return;}
 if(schema.required&&typeOk(value,"object"))for(const key of schema.required)if(!(key in value))errors.push({path:at+"/"+key,message:"is required"});
 if(schema.pattern&&typeof value==="string"&&!new RegExp(schema.pattern).test(value))errors.push({path:at,message:"does not match the declared pattern"});
 if(schema.minLength!==undefined&&typeof value==="string"&&value.length<schema.minLength)errors.push({path:at,message:"is shorter than the minimum length"});
 if(schema.minimum!==undefined&&typeof value==="number"&&value<schema.minimum)errors.push({path:at,message:"is below the minimum"});
 if(schema.maximum!==undefined&&typeof value==="number"&&value>schema.maximum)errors.push({path:at,message:"is above the maximum"});
 if(schema.minItems!==undefined&&Array.isArray(value)&&value.length<schema.minItems)errors.push({path:at,message:"has too few items"});
 if(Array.isArray(value)&&schema.items)value.forEach((item,i)=>walk(schema.items,item,at+"/"+i,errors));
 if(typeOk(value,"object")&&schema.properties){const allowed=new Set(Object.keys(schema.properties));for(const key of Object.keys(value))if(schema.additionalProperties===false&&!allowed.has(key))errors.push({path:at+"/"+key,message:"is not declared"});for(const key of Object.keys(schema.properties))if(key in value)walk(schema.properties[key],value[key],at+"/"+key,errors);}
}
export function validateAgainstSchema(schema,value){const errors=[];walk(schema,value,"",errors);return {valid:errors.length===0,errors};}
export function loadSchema(relativePath){const full=path.resolve(schemaRoot,relativePath);if(!full.startsWith(schemaRoot+path.sep))throw new Error("schema path escapes schema root");return JSON.parse(fs.readFileSync(full,"utf8"));}
export function validateArtifact(relativePath,artifact){return validateAgainstSchema(loadSchema(relativePath),artifact);}
