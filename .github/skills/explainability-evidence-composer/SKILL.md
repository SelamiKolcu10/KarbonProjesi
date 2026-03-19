---
name: explainability-evidence-composer
description: "Compose regulator-grade evidence packages for every Auditor and Strategist numerical output, including formula, legal reference, source provenance, and traceable evidence-tree links. Use when generating audit trails, legal justifications, and non-black-box calculation narratives in CBAM workflows."
argument-hint: "Provide target outputs, formula sources, regulation references, and provenance requirements for evidence package generation"
user-invocable: true
disable-model-invocation: false
---

# Explainability Evidence Composer

## Purpose
This skill generates a mandatory, regulator-ready evidence package for each financial or mathematical output produced by Auditor and Strategist agents.

Primary outcomes:
- Remove black-box calculations from compliance reporting
- Attach legal and mathematical justification to each final value
- Link each result to a complete, backward-traceable evidence tree
- Support legal, audit, and compliance review with deterministic artifacts

## Scope
Applies to:
- Emission totals and breakdowns
- Carbon tax and liability outputs
- Strategist scenario projections and savings calculations
- Any derived metric shown in API, dashboard, or executive report

## Mandatory Rules
1. Mandatory justification package per final value
For every final numeric output, always include:
- Formula used (with concrete numeric substitution)
- CBAM legal/regulatory reference (article/annex)
- Source provenance pointer (document, page/sheet, row/line, field path)
- Deterministic calculation result and unit

2. No black-box steps
- Every intermediate and final step must be explainable.
- Hidden assumptions, implicit coefficients, and undocumented transforms are forbidden.
- If any step cannot be justified, output must be marked non-compliant.

3. Evidence tree linkage
- Every result must be attached to an evidence tree node.
- Every node must have parent links to upstream evidence (source data, formula, coefficient).
- Tree must support reverse tracing from final value to raw input origin.

## Canonical Evidence Package Contract
Each evidence package should include:
- evidence_id
- trace_id
- output_metric_name
- output_value
- output_unit
- formula_id
- formula_expression
- numeric_substitution
- legal_reference
- source_provenance_refs
- intermediate_steps
- evidence_tree_node_id
- generated_at
- composer_version

## Justification Format (Required)
For each final output metric, use this standard block:
1. Metric
- Name, value, unit

2. Formula
- Symbolic form
- Numeric substitution
- Rounded output with rounding policy

3. Legal basis
- Regulation identifier
- Article/Annex reference
- Optional legal note

4. Source provenance
- Source document id/name
- Location pointer (page/sheet and row/line)
- Source field path
- Extraction confidence (if available)

5. Trace links
- Parent evidence node ids
- Dependency coefficients and versions

## When To Use
Use this skill when:
- Producing regulator-facing audit trail output
- Publishing financial or emissions results to reports/APIs
- Reviewing explainability quality in Auditor/Strategist changes
- Investigating disputed calculations in compliance workflows
- Building legal review packets for external audit

Trigger words:
- explainability, audit trail, evidence package, legal justification, traceability, non-black-box, evidence tree

## Step-by-Step Procedure
1. Enumerate target outputs
- List every final numeric metric requiring evidence.
- Define mandatory fields and units per metric.

2. Resolve computation lineage
- Identify formula and coefficient versions used.
- Collect all intermediate steps from computation pipeline.

3. Attach legal references
- Map each formula to exact regulation clauses.
- Reject outputs lacking legal-reference mapping.

4. Attach source provenance
- Link each input operand to raw source pointers.
- Include extraction/mapping lineage where available.

5. Build evidence tree
- Create nodes for source, transform, formula, and final output.
- Ensure directed parent-child links and unique node ids.

6. Generate justification blocks
- Render formula with numeric substitution.
- Include rounding and precision policy notes.

7. Validate completeness
- Confirm no missing formula/legal/provenance/tree fields.
- Mark package compliant only if all checks pass.

8. Emit artifacts
- evidence_package.json (machine-readable)
- evidence_summary.md (human-readable)
- evidence_tree.json (graph structure)

## Required Decision Points
1. Missing legal reference
- If formula exists but legal reference missing: fail output as non-compliant.

2. Missing provenance
- If source pointer missing for required operand: fail output as non-compliant.

3. Derived-only metric
- If metric is derived from other derived metrics, include full dependency chain to raw source nodes.

4. Rounding boundary
- If rounding occurs, record exact stage and policy; hidden rounding is forbidden.

## Evidence Tree Model
Recommended node types:
- SOURCE_NODE: raw extracted input
- TRANSFORM_NODE: conversion/canonicalization step
- FORMULA_NODE: governed formula application
- OUTPUT_NODE: final reported metric

Each node should include:
- node_id
- node_type
- value and unit
- method/formula metadata
- provenance links
- parent_node_ids

## Compliance Failure Codes
Recommended codes:
- EVIDENCE_FORMULA_MISSING
- EVIDENCE_LEGAL_REFERENCE_MISSING
- EVIDENCE_PROVENANCE_MISSING
- EVIDENCE_TREE_BROKEN_LINK
- EVIDENCE_BLACK_BOX_STEP_DETECTED
- EVIDENCE_PRECISION_POLICY_MISSING

Each failure should include:
- code
- output_metric_name
- evidence_id
- trace_id
- message
- severity

## Quality Gates
An explainability package is complete only if all pass:
- Every final metric has a full justification block
- Formula and numeric substitution are both present
- Legal article/annex reference is present
- Source provenance pointers are complete
- Evidence tree path from output to source is traversable
- No black-box step remains

## Anti-Patterns
- Reporting only final numbers without formula substitution
- Referencing regulation at high level without article/annex specificity
- Omitting source row/line pointers
- Presenting derived results without parent evidence links
- Using narrative-only explanations without machine-readable artifacts

## Example Prompt Starters
- "Use explainability-evidence-composer to generate a full evidence package for effective liability and total emissions outputs."
- "Apply explainability-evidence-composer to verify there are no black-box steps in this Auditor report."
- "Use explainability-evidence-composer to build an evidence tree from Strategist projection outputs back to raw source rows."

## Output Contract For This Skill
When invoked, this skill should produce:
- Metric-level justification specification
- Evidence package schema for machine-readable audit use
- Evidence tree structure with linkage validation rules
- Compliance failure criteria for missing transparency fields
- Review checklist for legal and audit team approval
