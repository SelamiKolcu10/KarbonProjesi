---
name: reporting-payload-design-system
description: "Standardize DTO report payloads for Auditor and Strategist outputs, isolate backend calculation semantics from UI concerns, and enforce explainability/provenance confidence metadata for frontend and external consumers. Use when designing stable reporting schemas for integrations."
argument-hint: "Provide source audit/strategy outputs, target consumers, required metrics, and metadata obligations for DTO export"
user-invocable: true
disable-model-invocation: false
---

# Reporting Payload Design System

## Purpose
This skill defines a stable, integration-first reporting DTO system that transforms complex Auditor and Strategist outputs into standardized payloads for frontend and external systems.

Primary outcomes:
- Keep reporting contracts stable even when UI presentation changes
- Enforce mandatory explainability and confidence metadata in every report payload
- Export visualization-ready hierarchical JSON/Pydantic schemas with consistent naming

## Scope
Applies to:
- Auditor output to reporting DTO transformation
- Strategist output to reporting DTO transformation
- Frontend integration payloads (e.g., Eco-Simbios)
- External API/reporting consumers requiring stable contracts

## Mandatory Rules
1. Backend semantics must be isolated from UI representation
- Reporting DTO contracts are independent from UI component structure.
- UI redesign must not force DTO breaking changes.
- Backend computation semantics and UI formatting logic must remain decoupled.

2. Mandatory evidence and confidence metadata
- Every outbound report payload must embed explainability evidence references.
- Every outbound report payload must embed provenance/confidence metadata and confidence interval indicators.
- Missing evidence/confidence metadata makes report non-compliant.

3. Visualization-ready hierarchical schema
- Payload must be hierarchical, consistently named, and chart-friendly.
- Financial metrics, scenario comparisons, and regulation alerts must be first-class DTO sections.
- Use standardized JSON/Pydantic naming and explicit field typing.

## Dependency Contract
This skill depends on:
- explainability-evidence-composer (required evidence package linkage)
- data-provenance-confidence-calibration (required confidence/provenance metadata)
- agent-contract-registry (recommended DTO version governance)
- api-contract-consistency-guard (recommended external API drift protection)

If required evidence or confidence inputs are missing, DTO export is non-compliant.

## Canonical Reporting DTO Contract
Each report DTO should include:
- report_id
- report_version
- correlation_id
- generated_at
- reporting_period
- facility_context
- financial_metrics
- emissions_metrics
- scenario_comparison
- regulation_alerts
- explainability_metadata
- confidence_metadata
- export_metadata

## Naming and Structure Standard
1. Naming rules
- Use stable snake_case field names.
- Avoid UI-specific labels in contract fields.
- Keep semantic names domain-oriented (e.g., effective_liability_eur).

2. Section rules
- summary: high-level KPI block
- financial_metrics: liabilities, costs, stress outputs
- scenario_comparison: comparable scenario cards/tables
- regulation_alerts: legal/compliance warnings
- evidence: references and trace links
- confidence: quality and trust indicators

3. Typing rules
- Numeric fields use explicit units in field names or unit metadata.
- Optional fields must be marked explicitly and documented.
- Enumerations must be controlled and versioned.

## Explainability Metadata Contract
Required explainability fields:
- evidence_package_id
- evidence_tree_root_id
- key_metric_evidence_refs
- legal_reference_map
- explanation_status

Rules:
- Each key metric must map to at least one evidence reference.
- Evidence references must be resolvable and traceable.

## Confidence Metadata Contract
Required confidence fields:
- overall_data_confidence_score
- confidence_interval_by_metric
- low_confidence_field_count
- reviewed_override_count
- pending_review_count
- confidence_disclaimer

Rules:
- Confidence metadata must reflect latest approved review state.
- Confidence interval representation must be consistent across reports.

## Visualization-Ready Blocks
1. Financial block
- total_liability_eur
- effective_liability_eur
- liability_per_ton_eur
- stress_test_summary

2. Scenario block
- scenarios[] with capex_eur, opex_savings_eur, payback_years, roi_percent
- ranking_view and tie_break_policy

3. Regulation block
- alert_code
- severity
- impacted_metric_refs
- legal_reference

4. Trend/projection block (optional)
- yearly_projection[] with year, value_eur, delta_percent

## When To Use
Use this skill when:
- Creating or revising report DTO schemas
- Integrating backend outputs with frontend dashboards
- Exposing reports to external systems/APIs
- Standardizing naming and hierarchy for chart-ready output
- Preventing UI-driven payload drift

Trigger words:
- reporting dto, payload schema, frontend integration, chart-ready json, stable report contract, evidence metadata, confidence metadata

## Step-by-Step Procedure
1. Identify source outputs
- Collect Auditor and Strategist source models.
- Mark required metrics for downstream consumers.

2. Define canonical DTO schema
- Create stable report sections and typed fields.
- Apply naming and unit standards.

3. Map backend models to DTO
- Build explicit transformation mappings.
- Avoid passing raw internal models directly to UI.

4. Attach mandatory metadata
- Inject explainability evidence references.
- Inject confidence/provenance interval metrics.

5. Validate integration compatibility
- Validate DTO against agent-contract-registry version policy.
- Validate API exposure compatibility as needed.

6. Build comparable scenario view
- Normalize scenario outputs into one comparable schema.
- Include ROI/payback and ranking metadata.

7. Emit final payload package
- Export machine-readable JSON/Pydantic payload.
- Include version and trace metadata for replay/audit.

## Required Decision Points
1. Contract evolution strategy
- Additive optional field changes preferred.
- Breaking structural changes require report_version bump and migration notes.

2. Metric granularity
- Decide which metrics are summary-only versus full breakdown.
- Ensure consistency across all report consumers.

3. Confidence disclosure level
- Executive view: aggregated confidence indicators.
- Audit view: metric-level confidence and lineage references.

4. UI adaptation boundary
- UI-specific derived display fields should live in adapter layer, not canonical DTO.

## Compliance Failure Codes
Recommended codes:
- REPORT_DTO_SCHEMA_INVALID
- REPORT_DTO_EVIDENCE_METADATA_MISSING
- REPORT_DTO_CONFIDENCE_METADATA_MISSING
- REPORT_DTO_SECTION_NONCOMPARABLE
- REPORT_DTO_VERSIONING_POLICY_VIOLATION
- REPORT_DTO_UI_COUPLING_DETECTED

Each failure should include:
- code
- report_section
- expected_condition
- actual_condition
- severity
- trace_id

## Quality Gates
A reporting payload design is complete only if all pass:
- DTO schema is UI-agnostic and versioned
- Explainability metadata is present and linked
- Confidence metadata and intervals are present
- Financial/scenario/regulation sections are comparable and typed
- Naming conventions and unit semantics are consistent
- Consumer compatibility checks pass for target integrations

## Anti-Patterns
- Exposing internal backend models directly as API report contracts
- Embedding UI component structure into DTO schema
- Shipping report payload without evidence or confidence metadata
- Inconsistent field naming across report sections
- Mixing display formatting strings with raw numeric metrics

## Example Prompt Starters
- "Use reporting-payload-design-system to design a stable DTO for Auditor and Strategist outputs with evidence and confidence metadata."
- "Apply reporting-payload-design-system to normalize scenario comparison blocks for frontend chart rendering."
- "Use reporting-payload-design-system to decouple UI changes from report payload contract evolution."

## Output Contract For This Skill
When invoked, this skill should produce:
- Canonical report DTO schema specification
- Mapping plan from source models to DTO sections
- Mandatory evidence/confidence metadata checklist
- Comparable scenario and financial block blueprint
- Versioning and integration compatibility guidance
