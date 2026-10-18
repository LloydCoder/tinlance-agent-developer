import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const manifest = JSON.parse(fs.readFileSync("docs/ecosystem/ecosystem-manifest.json", "utf8"));
const replicas = JSON.parse(fs.readFileSync("docs/ecosystem/replication-manifest.json", "utf8"));

test("canonical P10 recovery certification remains serial and production-honest", () => {
  const state = manifest.certification_state;
  assert.equal(state.p0, "certified");
  assert.equal(state.p9, "certified");
  assert.equal(state.p10, "certified");
  assert.equal(state.sequence_release, "p10_complete");
  assert.equal(state.production, "unverified");
  assert.match(state.note, /repository-certified/i);
  assert.match(state.note, /production.*unverified/i);
});

test("P10 recovery gate and documentation define external production boundary", () => {
  const doc = fs.readFileSync("docs/ecosystem/P10-RECOVERY-CERTIFICATION.md", "utf8");
  const script = fs.readFileSync("scripts/p10_recovery_conformance.py", "utf8");
  assert.match(doc, /exact-lock/i);
  assert.match(doc, /RTO/i);
  assert.match(doc, /RPO/i);
  assert.match(doc, /external deployment evidence/i);
  assert.match(script, /RecoveryGate/);
  assert.match(script, /production.*unverified/i);
});

test("P10 replication fixture preserves tenant/workspace isolation", () => {
  assert.equal(replicas.schema, "replication/v1");
  assert.equal(replicas.authority_plane, "platform");
  assert.equal(replicas.replicas.length, 2);
  for (const field of ["id", "tenant_id", "workspace_id"]) {
    const values = replicas.replicas.map((replica) => replica[field]);
    assert.equal(new Set(values).size, 2, field);
    assert.ok(values.every((value) => typeof value === "string" && value.trim()));
  }
});
