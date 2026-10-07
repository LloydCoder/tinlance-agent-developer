#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const fail = (message) => { console.error("ecosystem validation: FAIL:", message); process.exit(1); };
const isSha = (value) => typeof value === "string" && /^[0-9a-f]{40}$/.test(value);

const lock = readJson("ecosystem.lock.json");
const manifest = readJson("docs/ecosystem/ecosystem-manifest.json");

if (lock.schema !== "tinlance-agent-ecosystem-lock/v1") fail("unexpected lock schema");
if (manifest.schema !== "tinlance-agent-system-manifest/v1") fail("unexpected manifest schema");
if (lock.baseline_id !== manifest.baseline_id) fail("baseline IDs differ");
if (!/^P(?:0|[1-9]|10)$/.test(manifest.phase)) fail("unsupported ecosystem baseline phase");
if (lock.contracts.platform_api !== manifest.contracts.platform_api) fail("Platform API versions differ");
if (lock.contracts.governed_execution !== manifest.contracts.governed_execution) fail("governed execution contracts differ");
if (lock.contracts.endpoint !== manifest.contracts.endpoint) fail("Platform endpoints differ");

const lockEntries = Object.entries(lock.repositories);
if (lockEntries.length !== 4) fail("ecosystem lock must contain exactly four repositories");
const ids = new Set();
const refs = new Set();
for (const [id, entry] of lockEntries) {
  if (ids.has(id)) fail(`duplicate repository id: ${id}`);
  ids.add(id);
  if (!entry.repository || !entry.role || !isSha(entry.ref)) fail(`incomplete lock entry: ${id}`);
  if (refs.has(entry.ref)) fail(`duplicate reviewed SHA: ${entry.ref}`);
  refs.add(entry.ref);
  const manifestEntry = manifest.repositories.find((item) => item.id === id);
  if (!manifestEntry) fail(`manifest missing repository: ${id}`);
  if (manifestEntry.repository !== entry.repository) fail(`repository mismatch: ${id}`);
  if (manifestEntry.reviewed_sha !== entry.ref) fail(`reviewed SHA mismatch: ${id}`);
  if (manifestEntry.role !== entry.role) fail(`role mismatch: ${id}`);
}
if (manifest.repositories.length !== 4) fail("manifest must contain exactly four repositories");

const platform = manifest.repositories.find((item) => item.id === "platform");
if (!platform || !platform.authority.includes("sole authority")) fail("Platform sole-authority statement is missing");
if (!manifest.authority_law.includes("authenticated principal") || !manifest.authority_law.includes("execution context")) {
  fail("effective-authority invariant is incomplete");
}
if (manifest.phase === "P1" && manifest.contracts.transformation_schema !== "transformation/v1") fail("P1 transformation contract version is missing");
if (manifest.phase === "P1" && !manifest.transformation_contract) fail("P1 transformation contract manifest is missing");
if (manifest.phase === "P10") {
  if (manifest.contracts.replication_schema !== "replication/v1") fail("P10 replication contract version is missing");
  if (!manifest.replication_contract) fail("P10 replication contract manifest is missing");
  if (manifest.replication_contract.replicas?.length !== 2) fail("P10 requires exactly two replication fixtures");
  const replicaIds = new Set(manifest.replication_contract.replicas.map((replica) => replica.id));
  const tenantIds = new Set(manifest.replication_contract.replicas.map((replica) => replica.tenant_id));
  if (replicaIds.size !== 2 || tenantIds.size !== 2) fail("P10 replicas and tenant IDs must be unique");
  if (manifest.replication_contract.authority_plane !== "platform") fail("P10 authority plane must remain Platform");
}
if (manifest.gate.repository_ci !== "required" ||
    manifest.gate.security_workflows !== "required" ||
    manifest.gate.ecosystem_conformance !== "required" ||
    manifest.gate.full_sha_pinning !== "required") {
  fail("mandatory P0 release gates are incomplete");
}
console.log("ecosystem validation: PASS");
