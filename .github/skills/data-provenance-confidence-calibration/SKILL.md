---
name: data-provenance-confidence-calibration
description: "Manage immutable field-level provenance, confidence calibration, and manual override lineage across Data Miner, Auditor, and Strategist workflows. Use when enforcing human-in-the-loop review for low-confidence extraction and exposing confidence metrics in explainable financial reporting."
argument-hint: "Provide source document metadata, confidence thresholds, human-review policy, and override audit requirements"
user-invocable: true
disable-model-invocation: false
---

# Data Provenance and Confidence Calibration

## Purpose
This skill defines strict, immutable governance for field-level provenance, extraction confidence calibration, and manual override history in CBAM workflows.

Primary outcomes:
- Track origin of every data field (document/page/row)
- Enforce deterministic confidence scoring and low-confidence review routing
- Preserve tamper-evident override history for audit and legal defensibility

## Scope
Applies to:
- Data Miner extraction outputs
- Mapped payload fields entering Auditor
- Strategist and reporting confidence disclosures
- Human-in-the-loop review and manual corrections
- Explainability evidence packages and final financial reports

## Mandatory Rules
1. Deterministic confidence assignment and review gating
- Every extracted field must have a deterministic confidence score.
- Confidence below threshold must be routed to manual approval queue before calculation.
- Low-confidence values cannot silently pass into financial calculations.

2. Confidence-aware calculation and reporting
- Auditor and Strategist must reference field confidence in explainability outputs.
- Final reports must include confidence metrics or confidence intervals.
- Confidence provenance must be linked to explainability-evidence-composer artifacts.

3. Immutable override audit trail
- Every manual override must store old value, new value, actor, reason, and timestamp.
- Override records must be append-only and traceable.
- Deleting or rewriting historical override events is forbidden.

## Dependency Contract
This skill depends on:
- explainability-evidence-composer (required for confidence-linked evidence)
- payload-mapping-canonicalization (source lineage continuity)
- data-quality-rule-engine (optional low-confidence policy coupling)

If explainability linkage is missing, confidence governance is non-compliant.

## Field Provenance Contract
Each extracted/mapped field should include:
- field_id
- canonical_field_name
- source_document_id
- source_document_name
- source_locator (page/sheet + row/line)
- source_path
- extracted_value
- extracted_unit
- canonical_value
- canonical_unit
- extraction_method
- extracted_at
- trace_id

## Confidence Calibration Contract
Each field confidence record should include:
- confidence_score (0.0 - 1.0)
- confidence_model_version
- scoring_features_used
- threshold_profile_id
- threshold_value
- confidence_status (HIGH, MEDIUM, LOW, REQUIRES_REVIEW)
- calibration_version

Required scoring rules:
- Same input and model version must produce same confidence score.
- Threshold policy must be versioned and centrally managed.
- Confidence status must be derived deterministically from threshold profile.

## Human-in-the-Loop Queue Policy
Queue trigger conditions:
- confidence_score < threshold_value
- conflicting extraction candidates
- critical field with uncertain provenance

Queue record should include:
- review_ticket_id
- field_id
- proposed_value
- confidence_score
- trigger_reason
- created_at
- status (PENDING_REVIEW, APPROVED, REJECTED, ESCALATED)

Blocking rule:
- If critical fields are pending review, downstream audit computation must pause.

## Override Audit Contract
Each manual override event must include:
- override_id
- field_id
- previous_value
- new_value
- changed_by
- changed_at
- change_reason
- approval_reference (optional)
- correlation_id
- trace_id

Immutability requirements:
- Override log is append-only.
- Corrections to corrections create new events.
- Historical values remain queryable for replay and audit.

## When To Use
Use this skill when:
- Implementing extraction confidence logic
- Routing uncertain values to human review
- Auditing manual data corrections
- Publishing confidence-aware financial reports
- Investigating disputes on data trustworthiness

Trigger words:
- data provenance, confidence score, human in the loop, manual override, audit trail, confidence interval, field lineage

## Step-by-Step Procedure
1. Capture field lineage at extraction
- Attach source document/page/row metadata to every extracted field.
- Preserve lineage through mapping and canonicalization.

2. Compute confidence deterministically
- Run governed confidence scoring model.
- Assign confidence status by threshold profile.

3. Apply review gate
- Route low-confidence critical fields to manual queue.
- Block dependent computations until review outcome is resolved.

4. Execute downstream calculations with confidence context
- Pass confidence metadata to Auditor and Strategist inputs.
- Require explainability references to confidence artifacts.

5. Record manual overrides immutably
- Log previous/new values, actor, and reason.
- Maintain append-only change history.

6. Emit confidence-aware outputs
- Include confidence metrics/intervals in final reports.
- Include data trust summary for management-level decisions.

7. Validate audit completeness
- Ensure provenance, confidence, and override artifacts are present and linked.

## Required Decision Points
1. Critical field policy
- Define which fields are critical and block computation when confidence is low.

2. Threshold profile selection
- Use sector/reporting-context profile; avoid ad hoc threshold tuning.

3. Override approval flow
- Decide which overrides require second-level approval.
- Mark unapproved overrides as provisional and non-final.

4. Confidence disclosure granularity
- Field-level for audit trails
- Aggregated metric-level for executive reports

## Confidence Reporting Contract
Final financial/compliance report should include:
- overall_data_confidence_score
- confidence_interval_by_key_metric
- low-confidence_field_count
- reviewed_override_count
- pending_review_count
- confidence_disclaimer

Explainability linkage requirements:
- Each key reported metric must reference contributing field confidence profiles.
- Confidence disclosures must map to evidence nodes in explainability-evidence-composer.

## Compliance Failure Codes
Recommended codes:
- PROV_FIELD_LINEAGE_MISSING
- CONF_SCORE_NOT_CALCULATED
- CONF_LOW_CONFIDENCE_UNREVIEWED
- CONF_EXPLAINABILITY_LINK_MISSING
- OVERRIDE_AUDIT_RECORD_MISSING
- OVERRIDE_IMMUTABILITY_VIOLATION

Each failure should include:
- code
- field_id or metric_name
- expected_condition
- actual_condition
- severity
- trace_id

## Quality Gates
A provenance/confidence workflow is complete only if all pass:
- Field-level provenance exists for all required data points
- Confidence scores are deterministic and thresholded
- Low-confidence critical fields are reviewed before computation
- Override events are append-only and fully attributed
- Final reports include confidence metrics and explainability links

## Anti-Patterns
- Computing final liability with unresolved low-confidence critical inputs
- Storing confidence score without model/threshold version
- Overwriting old values instead of appending override events
- Reporting confidence as vague text without numeric basis
- Breaking provenance chain between extraction and reporting layers

## Example Prompt Starters
- "Use data-provenance-confidence-calibration to design field-level provenance and confidence gating for Data Miner outputs."
- "Apply data-provenance-confidence-calibration to enforce manual review queue on low-confidence critical fields before Auditor calculations."
- "Use data-provenance-confidence-calibration to add immutable override logs and confidence disclosures to executive reports."

## Output Contract For This Skill
When invoked, this skill should produce:
- Field-level provenance schema and lineage policy
- Confidence scoring and threshold gating specification
- Human-in-the-loop queue decision contract
- Immutable override audit model
- Confidence-aware reporting checklist with explainability links
