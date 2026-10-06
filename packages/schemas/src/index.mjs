import fs from "node:fs";
import path from "node:path";

const schemaRoot = path.resolve(process.cwd(), "schemas");
const schemaCache = new Map();

function typeOk(value, expected) {
  if (Array.isArray(expected)) return expected.some((item) => typeOk(value, item));
  switch (expected) {
    case "object": return typeof value === "object" && value !== null && !Array.isArray(value);
    case "array": return Array.isArray(value);
    case "string": return typeof value === "string";
    case "number": return typeof value === "number" && Number.isFinite(value);
    case "integer": return typeof value === "number" && Number.isInteger(value);
    case "boolean": return typeof value === "boolean";
    case "null": return value === null;
    default: return true;
  }
}

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;
  if (typeof a !== typeof b) return false;
  if (Array.isArray(a) || Array.isArray(b)) return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((v, i) => deepEqual(v, b[i]));
  if (a && b && typeof a === "object") {
    const ak = Object.keys(a).sort(), bk = Object.keys(b).sort();
    return ak.length === bk.length && ak.every((k, i) => k === bk[i] && deepEqual(a[k], b[k]));
  }
  return false;
}

function pointerUnescape(segment) { return segment.replace(/~1/g, "/").replace(/~0/g, "~"); }

function resolvePointer(root, pointer) {
  if (pointer === "" || pointer === "#") return root;
  const raw = pointer.startsWith("#") ? decodeURIComponent(pointer.slice(1)) : pointer;
  if (!raw.startsWith("/")) throw new Error("Only JSON Pointer references are supported");
  return raw.slice(1).split("/").map(pointerUnescape).reduce((value, key) => {
    if (value === undefined || value === null || !(key in value)) throw new Error("Unresolvable JSON Pointer: " + pointer);
    return value[key];
  }, root);
}

function formatOk(value, format) {
  if (typeof value !== "string") return true;
  switch (format) {
    case "date": return /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value + "T00:00:00Z"));
    case "time": return /^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-][0-2]\d:[0-5]\d)$/.test(value);
    case "date-time": return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value);
    case "duration": return /^P(?!$)(?:\d+Y)?(?:\d+M)?(?:\d+D)?(?:T(?=\d)(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$/.test(value);
    case "email": return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    case "ipv4": return /^\d{1,3}(?:\.\d{1,3}){3}$/.test(value) && value.split(".").every((x) => Number(x) <= 255);
    case "ipv6": return /^[0-9A-Fa-f:]+$/.test(value) && value.includes(":");
    case "uuid": return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
    case "uri":
    case "uri-reference":
    case "iri":
    case "iri-reference":
      try { new URL(value, "https://tadl.invalid"); return true; } catch { return false; }
    case "regex":
      try { new RegExp(value); return true; } catch { return false; }
    case "json-pointer": return value === "" || /^(?:\/(?:[^~/]|~[01])*)*$/.test(value);
    case "relative-json-pointer": return /^(?:0|[1-9]\d*)(?:#|(?:\/(?:[^~/]|~[01])*)*)$/.test(value);
    case "hostname": return value.length <= 253 && /^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$/.test(value);
    default: return true;
  }
}

function loadSchemaDocument(relativePath) {
  const full = path.resolve(schemaRoot, relativePath);
  if (!full.startsWith(schemaRoot + path.sep)) throw new Error("schema path escapes schema root");
  if (!schemaCache.has(full)) schemaCache.set(full, JSON.parse(fs.readFileSync(full, "utf8")));
  return schemaCache.get(full);
}

function validate(schema, value, root, at, errors, state) {
  if (!schema || typeof schema !== "object") return;

  if (schema.$ref) {
    const target = resolvePointer(root, schema.$ref);
    const refKey = schema.$ref + "|" + at;
    if (state.refs.has(refKey)) return;
    state.refs.add(refKey);
    validate(target, value, root, at, errors, state);
    state.refs.delete(refKey);
    return;
  }

  if (schema.allOf) schema.allOf.forEach((s) => validate(s, value, root, at, errors, state));

  if (schema.anyOf) {
    const branches = schema.anyOf.map((s) => {
      const branchErrors = [];
      validate(s, value, root, at, branchErrors, {...state, refs: new Set(state.refs)});
      return branchErrors;
    });
    if (!branches.some((branch) => branch.length === 0)) errors.push({path: at, message: "must satisfy at least one anyOf branch"});
  }

  if (schema.oneOf) {
    const matches = schema.oneOf.filter((s) => {
      const branchErrors = [];
      validate(s, value, root, at, branchErrors, {...state, refs: new Set(state.refs)});
      return branchErrors.length === 0;
    }).length;
    if (matches !== 1) errors.push({path: at, message: "must satisfy exactly one oneOf branch"});
  }

  if (schema.not) {
    const branchErrors = [];
    validate(schema.not, value, root, at, branchErrors, {...state, refs: new Set(state.refs)});
    if (branchErrors.length === 0) errors.push({path: at, message: "must not satisfy the not schema"});
  }

  if (schema.if) {
    const conditionErrors = [];
    validate(schema.if, value, root, at, conditionErrors, {...state, refs: new Set(state.refs)});
    if (conditionErrors.length === 0 && schema.then) validate(schema.then, value, root, at, errors, state);
    if (conditionErrors.length !== 0 && schema.else) validate(schema.else, value, root, at, errors, state);
  }

  if (schema.const !== undefined && !deepEqual(value, schema.const)) errors.push({path: at, message: "must equal the declared constant"});
  if (schema.enum && !schema.enum.some((item) => deepEqual(item, value))) errors.push({path: at, message: "must be one of the declared enum values"});

  if (schema.type && !typeOk(value, schema.type)) {
    errors.push({path: at, message: "has the wrong type"});
    return;
  }

  if (typeof value === "string") {
    if (schema.minLength !== undefined && [...value].length < schema.minLength) errors.push({path: at, message: "is shorter than minLength"});
    if (schema.maxLength !== undefined && [...value].length > schema.maxLength) errors.push({path: at, message: "is longer than maxLength"});
    if (schema.pattern !== undefined) {
      let matches = false;
      try { matches = new RegExp(schema.pattern).test(value); } catch { errors.push({path: at, message: "declared pattern is invalid"}); }
      if (!matches) errors.push({path: at, message: "does not match the declared pattern"});
    }
    if (schema.format && !formatOk(value, schema.format)) errors.push({path: at, message: "does not satisfy format " + schema.format});
  }

  if (typeof value === "number") {
    if (schema.multipleOf !== undefined && Math.abs(value / schema.multipleOf - Math.round(value / schema.multipleOf)) > Number.EPSILON) errors.push({path: at, message: "is not a multipleOf the declared value"});
    if (schema.minimum !== undefined && value < schema.minimum) errors.push({path: at, message: "is below minimum"});
    if (schema.maximum !== undefined && value > schema.maximum) errors.push({path: at, message: "is above maximum"});
    if (typeof schema.exclusiveMinimum === "number" && value <= schema.exclusiveMinimum) errors.push({path: at, message: "is not above exclusiveMinimum"});
    if (typeof schema.exclusiveMaximum === "number" && value >= schema.exclusiveMaximum) errors.push({path: at, message: "is not below exclusiveMaximum"});
  }

  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) errors.push({path: at, message: "has too few items"});
    if (schema.maxItems !== undefined && value.length > schema.maxItems) errors.push({path: at, message: "has too many items"});
    if (schema.uniqueItems) {
      for (let i = 0; i < value.length; i++) for (let j = i + 1; j < value.length; j++) if (deepEqual(value[i], value[j])) errors.push({path: at, message: "must contain unique items"});
    }
    if (schema.prefixItems) schema.prefixItems.forEach((s, i) => { if (i < value.length) validate(s, value[i], root, at + "/" + i, errors, state); });
    if (schema.items && !Array.isArray(schema.items)) {
      const start = Array.isArray(schema.prefixItems) ? schema.prefixItems.length : 0;
      value.slice(start).forEach((item, i) => validate(schema.items, item, root, at + "/" + (i + start), errors, state));
    }
    if (schema.contains) {
      const matches = value.filter((item, i) => {
        const branchErrors = [];
        validate(schema.contains, item, root, at + "/" + i, branchErrors, {...state, refs: new Set(state.refs)});
        return branchErrors.length === 0;
      }).length;
      if (matches === 0 || (schema.minContains !== undefined && matches < schema.minContains) || (schema.maxContains !== undefined && matches > schema.maxContains)) errors.push({path: at, message: "does not satisfy contains constraints"});
    }
  }

  if (value && typeof value === "object" && !Array.isArray(value)) {
    const properties = schema.properties ?? {};
    const evaluated = new Set(Object.keys(properties));
    if (schema.required) for (const key of schema.required) if (!(key in value)) errors.push({path: at + "/" + key, message: "is required"});
    for (const [key, childSchema] of Object.entries(properties)) if (key in value) validate(childSchema, value[key], root, at + "/" + key.replace(/~/g, "~0").replace(/\//g, "~1"), errors, state);
    const patterns = schema.patternProperties ?? {};
    for (const key of Object.keys(value)) for (const [pattern, childSchema] of Object.entries(patterns)) if (new RegExp(pattern).test(key)) { evaluated.add(key); validate(childSchema, value[key], root, at + "/" + key, errors, state); }
    const unevaluated = Object.keys(value).filter((key) => !evaluated.has(key));
    if (schema.additionalProperties === false && unevaluated.length) for (const key of unevaluated) errors.push({path: at + "/" + key, message: "is not declared"});
    else if (schema.additionalProperties && typeof schema.additionalProperties === "object") for (const key of unevaluated) validate(schema.additionalProperties, value[key], root, at + "/" + key, errors, state);
    if (schema.propertyNames) for (const key of Object.keys(value)) validate(schema.propertyNames, key, root, at + "/<propertyName>", errors, state);
    if (schema.minProperties !== undefined && Object.keys(value).length < schema.minProperties) errors.push({path: at, message: "has too few properties"});
    if (schema.maxProperties !== undefined && Object.keys(value).length > schema.maxProperties) errors.push({path: at, message: "has too many properties"});
    if (schema.dependentRequired) for (const [key, required] of Object.entries(schema.dependentRequired)) if (key in value) for (const dep of required) if (!(dep in value)) errors.push({path: at + "/" + dep, message: "is required when " + key + " is present"});
    if (schema.dependentSchemas) for (const [key, childSchema] of Object.entries(schema.dependentSchemas)) if (key in value) validate(childSchema, value, root, at, errors, state);
  }
}

export function validateAgainstSchema(schema, value) {
  const errors = [];
  validate(schema, value, schema, "", errors, {refs: new Set()});
  return {valid: errors.length === 0, errors};
}

export function loadSchema(relativePath) { return loadSchemaDocument(relativePath); }
export function validateArtifact(relativePath, artifact) { return validateAgainstSchema(loadSchema(relativePath), artifact); }
