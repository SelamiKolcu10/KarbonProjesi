---
name: multi-format-ingestion-assurance
description: "Apply format-specific quality controls and resilient fallback hierarchies for heterogeneous Data Miner inputs (PDF, Excel, CSV, OCR). Use when hardening ingestion reliability, isolating parsing complexity, and reporting failures with agent-messaging-error-taxonomy contracts."
argument-hint: "Provide file types, expected extraction fields, fallback order, and validation/error-reporting requirements"
user-invocable: true
disable-model-invocation: false
---

# Multi-Format Ingestion Assurance

## Purpose
This skill enforces robust, format-aware ingestion standards for Data Miner across heterogeneous external inputs, while keeping parsing concerns isolated from central math and orchestration layers.

Primary outcomes:
- Format-specific validation for PDF/Excel/CSV/OCR pipelines
- Structured fallback hierarchy to prevent ingestion collapse
- Strict separation of ingestion logic from carbon-math and orchestration logic

## Scope
Applies to:
- Raw file ingestion entrypoints
- Parsing and extraction pipelines for PDF, Excel, CSV, and OCR flows
- Ingestion failure handling and error reporting
- Pre-mapping quality checks before payload canonicalization

## Mandatory Rules
1. Format-specific validation strategy per file type
- Each format must have explicit validation checks before extraction.
- Generic one-size-fits-all parsing is not allowed.
- Validation outcomes must be machine-readable and traceable.

2. Structured fallback hierarchy and taxonomy-aligned errors
- On extractor failure, system must use deterministic fallback sequence.
- Failure reporting must conform to agent-messaging-error-taxonomy codes.
- Ingestion failure must degrade gracefully, not crash workflow silently.

3. Strict layer isolation
- Parsing and ingestion complexity must stay in ingestion boundary.
- No ingestion-specific parsing logic in carbon-math-governance code.
- No ingestion parsing branches embedded in orchestrator-lifecycle-reliability core state logic.

## Dependency Contract
This skill depends on:
- agent-messaging-error-taxonomy (required for standardized ingestion errors)
- payload-mapping-canonicalization (required for post-ingestion normalization)
- data-quality-rule-engine (optional for post-parse rule checks)
- orchestrator-lifecycle-reliability (optional for retry/dead-letter integration)
- carbon-math-governance (must remain isolated from ingestion parsing concerns)

If taxonomy mapping is missing, ingestion assurance result is non-compliant.

## Format Validation Standards
### PDF
Required checks:
- file readability and page count
- text layer presence detection
- table extractability signal (if expected)

If text layer missing/insufficient:
- auto-route to OCR pipeline
- mark extraction_method as OCR
- preserve confidence penalty metadata

### Excel (XLSX/XLS)
Required checks:
- sheet presence and readability
- header detection and column mapping quality
- mandatory field columns present
- empty-cell ratio on critical columns

If mandatory cells empty beyond threshold:
- fail or route to manual review by policy

### CSV
Required checks:
- encoding detection/validation
- delimiter detection consistency
- schema/header conformity
- malformed row ratio

If malformed ratio exceeds threshold:
- fail with structured ingestion error

### OCR Inputs (scanned docs/images)
Required checks:
- image/page quality signal
- OCR confidence distribution
- language/script detection consistency
- character noise ratio

If OCR confidence below critical threshold:
- route to human review queue before downstream use

## Fallback Hierarchy Contract
Recommended fallback order:
1. Primary parser (format-native)
2. Secondary parser/alternate library
3. OCR-assisted extraction (for PDF/image-like failure cases)
4. Partial extraction with explicit missing-field flags
5. Human-in-the-loop escalation

Rules:
- Fallback order must be deterministic and configurable.
- Each fallback attempt must be logged with attempt index and reason.
- Final failure must produce taxonomy-compliant error event.

## Ingestion Error Contract
Each ingestion failure event should include:
- event_id
- correlation_id
- file_id/file_name
- format_type
- stage (read, parse, extract, validate)
- error_code
- severity
- fallback_attempted
- fallback_stage
- message
- diagnostics
- trace_id
- occurred_at

Recommended error codes:
- INGEST_FILE_UNREADABLE
- INGEST_FORMAT_NOT_SUPPORTED
- INGEST_PDF_TEXT_LAYER_MISSING
- INGEST_OCR_CONFIDENCE_LOW
- INGEST_EXCEL_REQUIRED_COLUMN_MISSING
- INGEST_CSV_SCHEMA_MISMATCH
- INGEST_MALFORMED_ROWS_EXCEEDED
- INGEST_FALLBACK_EXHAUSTED

## Isolation Architecture Rules
1. Ingestion boundary responsibilities
- File I/O, parser selection, extraction heuristics, fallback control, and raw quality checks.

2. Mapping boundary responsibilities
- Canonical transformation and unit normalization after ingestion output stabilization.

3. Math boundary responsibilities
- Only approved deterministic formulas; never raw file parsing or extraction heuristics.

4. Orchestration boundary responsibilities
- Job/state/retry flow control; no format-specific parsing decisions embedded in state machine transitions.

## When To Use
Use this skill when:
- Adding support for new file format variants
- Hardening ingestion against malformed/low-quality documents
- Standardizing fallback behavior and error emission
- Refactoring parser logic out of core orchestration or math layers

Trigger words:
- ingestion assurance, pdf ocr fallback, excel validation, csv schema check, parser resilience, extraction failure handling

## Step-by-Step Procedure
1. Identify incoming format portfolio
- List all accepted formats and expected extraction targets.

2. Define format-specific validation matrix
- Specify per-format checks, thresholds, and blocking criteria.

3. Define fallback hierarchy
- Declare deterministic fallback order and stop conditions.

4. Implement taxonomy-aligned errors
- Map each ingestion failure mode to stable error codes and severity.

5. Enforce layer isolation
- Confirm parsing logic stays outside math/orchestration core code.

6. Validate robustness
- Test success, degraded, and failure paths per format.
- Verify no silent failure and no uncontrolled crash.

7. Publish assurance artifacts
- Emit machine-readable ingestion quality report.
- Emit per-file extraction and fallback trace summary.

## Required Decision Points
1. Block vs continue with partial data
- Critical missing fields: block or escalate to review queue.
- Non-critical missing fields: allow with explicit flags and reduced confidence.

2. Fallback exhaustion behavior
- If all fallbacks fail: produce INGEST_FALLBACK_EXHAUSTED and route by orchestration policy.

3. Human review trigger policy
- Define confidence/quality thresholds for mandatory manual review.

## Quality Gates
An ingestion assurance implementation is complete only if all pass:
- Format-specific validation matrix implemented
- Deterministic fallback hierarchy configured
- Taxonomy-aligned error events emitted
- Parsing logic isolated from math and orchestrator core
- Test coverage includes success/fallback/exhaustion for each supported format

## Anti-Patterns
- Treating all file formats with same parser assumptions
- Failing hard without fallback attempt records
- Emitting generic exceptions without taxonomy error codes
- Embedding parser branches inside carbon math calculations
- Mixing ingestion heuristics into orchestrator state transition logic

## Example Prompt Starters
- "Use multi-format-ingestion-assurance to define PDF text-layer checks with OCR fallback and taxonomy-compliant failure reporting."
- "Apply multi-format-ingestion-assurance to add Excel empty-cell threshold validation and manual review routing."
- "Use multi-format-ingestion-assurance to isolate parsing logic from orchestrator and carbon math boundaries."

## Output Contract For This Skill
When invoked, this skill should produce:
- Format-specific validation matrix
- Deterministic fallback hierarchy specification
- Ingestion error taxonomy mapping table
- Layer-isolation architecture checklist
- Robustness test plan for ingestion success/degradation/failure paths
