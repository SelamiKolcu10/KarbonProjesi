---
name: payload-mapping-canonicalization
description: "Map raw Data Miner outputs into canonical Auditor payloads with strict unit conversion, null-safe error handling, and full data provenance logging. Use when transforming extraction JSON, standardizing units (kg/lbs/kWh/m3), validating required fields, and preventing mapping drift in CBAM workflows."
argument-hint: "Provide raw payload sample, target auditor model, source units, required fields, and expected provenance granularity"
user-invocable: true
disable-model-invocation: false
---

# Payload Mapping and Canonicalization

## Purpose
This skill standardizes raw upstream data into a deterministic, validated, and traceable payload for Auditor ingestion.

Core outcomes:
- Convert heterogeneous source units into canonical system units
- Preserve strict analytic behavior for missing or invalid data
- Produce auditable provenance for every transformed field
- Prevent mapper drift between extraction output and Auditor contract

## Canonical Target Units
Use these canonical units at system boundaries:
- Mass: tons
- Energy: MWh
- Volume (natural gas): m3

No non-canonical unit is allowed in final Auditor input payload.

## Mandatory Rules
1. Deterministic unit conversion only
- All external units must be converted mathematically.
- No heuristic, approximate, or guessed conversion is allowed.
- Every conversion must be reproducible from formula and factor.

2. Null-safe strictness
- Never infer missing values from context.
- Missing required value must raise a structured analytic error.
- Optional null values may pass only if contract explicitly allows null.

3. Full provenance logging
- Each mapped field must include source pointer metadata.
- Minimum provenance: source document id/name, page/sheet, row/line, extractor confidence (if available).
- Derived fields must include derivation formula and source field references.

## When To Use
Use this skill when:
- Mapping Data Miner JSON into Auditor InputPayload
- Introducing a new source file type or extraction schema
- Adding/changing units in source systems
- Investigating mapping inconsistencies in emission/tax outputs
- Reviewing mapper changes for drift and traceability risk

Trigger words:
- mapping, canonicalization, unit conversion, payload adapter, provenance, null handling, schema drift

## Step-by-Step Procedure
1. Define source and target contracts
- Identify producer schema (Data Miner output).
- Identify consumer schema (Auditor input model).
- Mark each target field as required or optional.

2. Build field mapping matrix
- For each target field, declare source path(s), source unit, target unit, transform function, and error behavior.
- Example columns: target_field, source_path, required, source_unit, target_unit, transform, on_missing.

3. Apply canonical unit conversion
- Convert source values to canonical units using strict factors.
- Store conversion operation metadata (factor, formula, pre_value, post_value).

4. Run null and type validation
- If required field missing/null: raise CONTRACT_REQUIRED_FIELD_MISSING.
- If unit unknown or conversion unsupported: raise CANONICAL_UNIT_UNSUPPORTED.
- If type mismatch: raise CONTRACT_TYPE_MISMATCH.

5. Generate provenance bundle
- Attach source location metadata per target field.
- Attach derivation chain for transformed fields.
- Emit transformation log entry with timestamp and trace id.

6. Validate final payload against consumer model
- Parse with target Pydantic model.
- Reject if any field violates constraints.

7. Emit output package
- canonical_payload: strict consumer-ready payload
- mapping_report: field-level mapping summary
- provenance_log: complete source-to-target trace
- errors: structured error list (if any)

## Required Decision Points
1. Field requiredness decision
- If target field required and source unavailable: hard fail.
- If target field optional and source unavailable: keep null and record reason.

2. Multi-source conflict decision
- If multiple sources provide same field:
  - Prefer highest-confidence source if confidence exists.
  - Otherwise apply deterministic priority order declared in mapping matrix.
  - Always log rejected alternatives.

3. Conversion support decision
- If conversion pair is defined: convert and proceed.
- If conversion pair undefined: fail with CANONICAL_UNIT_UNSUPPORTED.

## Conversion Standard Table
Use exact factors (example baseline set):
- kg -> tons: value * 0.001
- lb -> tons: value * 0.000453592
- lbs -> tons: value * 0.000453592
- kWh -> MWh: value * 0.001
- GWh -> MWh: value * 1000
- mmbtu -> MWh: value * 0.293071
- sm3 -> m3: value * 1.0
- nm3 -> m3: value * 1.0
- mcf -> m3: value * 28.3168

If project constants define conversion values, those constants are authoritative.

## Structured Error Contract
Recommended error codes:
- CONTRACT_REQUIRED_FIELD_MISSING
- CONTRACT_TYPE_MISMATCH
- CANONICAL_UNIT_UNSUPPORTED
- CANONICAL_CONVERSION_OVERFLOW
- PROVENANCE_METADATA_MISSING
- MAPPING_SOURCE_PATH_NOT_FOUND

Each error should include:
- code
- message
- target_field
- source_path
- trace_id
- severity

## Provenance Contract
Per mapped field, capture at minimum:
- target_field
- source_document
- source_locator (page/sheet and row/line)
- source_path
- source_value
- source_unit
- canonical_value
- canonical_unit
- conversion_factor
- conversion_formula
- mapping_timestamp
- trace_id

## Quality Gates
A mapping change is complete only if all pass:
- Field mapping matrix is updated
- Required field behavior is explicitly tested
- Conversion formulas are covered by unit tests
- Unsupported unit path is tested
- Provenance is emitted for all mapped fields
- Consumer Pydantic validation passes
- Legacy source payload compatibility is verified

## Anti-Patterns
- Silent fallback to zero for missing required values
- Implicit unit assumptions without explicit source unit
- Dropping provenance for transformed fields
- Mixing canonical and non-canonical units in final payload
- Using guessed conversions or model-generated estimates

## Example Prompt Starters
- "Use payload-mapping-canonicalization to map this raw extraction JSON into Auditor payload with strict unit conversion and provenance logs."
- "Apply payload-mapping-canonicalization to add lbs and kWh support while preserving null-safe error handling."
- "Use payload-mapping-canonicalization to review mapper drift risks between Data Miner output and Auditor input."

## Output Contract For This Skill
When invoked, this skill should produce:
- Mapping plan and field matrix
- Canonical conversion plan with formulas
- Null/error handling behavior by field
- Provenance logging structure
- Validation and regression test checklist
