# P1 — Transformation Model

P1 introduces the first cross-repository business-to-execution object: a **Transformation**.

A Transformation answers, in one versioned record:

`intent → actor → context → requested capability → constraints → governance → execution → outputs → evidence → outcome`

It bridges developer intent and operational execution without moving authorization into the model.

## Authority rule

The Transformation is a data contract. It **never grants authority**.

The Platform independently authenticates the principal, binds the tenant, evaluates capability/policy/risk/approval/budget/sandbox/secret scope, and re-authorizes consequential side effects.

Model output, memory, retrieved content, tool output, peer-agent messages, registry metadata and Transformation fields are untrusted inputs until accepted by the authoritative Platform boundary.

## Lifecycle

A Transformation is versioned and append-oriented. A new state is represented by a new version; consumers must not mutate historical versions in place.

Execution state is operational state:

- planned
- running
- succeeded
- failed
- cancelled
- partial

Outcome status is deliberately separate from execution status:

- unknown
- achieved
- partially_achieved
- not_achieved
- inconclusive

This separation prevents a technically successful run from being mistaken for a successful business outcome.

## Evidence and provenance

Outputs and evidence are references, not authority. Where a digest is present it is a SHA-256 content digest. Provenance identifies who declared the record, when it was recorded, and its source references.

## Golden transformation

The P1 conformance path is:

`TADL declaration → Agent OS workspace/task → SDK transport → Platform governance/execution → authoritative evidence → OS result → Transformation outcome`

P1 is complete only when the same Transformation identity and version remain attributable across those boundaries.

## Machine-readable contract

- Schema: `schemas/transformation/v1/transformation.schema.json`
- Example: `schemas/examples/transformation.v1.json`

The schema is deliberately authority-neutral; authorization remains Platform-owned.
