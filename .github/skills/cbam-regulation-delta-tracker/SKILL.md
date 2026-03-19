---
name: cbam-regulation-delta-tracker
description: "Track article-level deltas in EU CBAM regulations, map their system impact on carbon math, data quality rules, and reporting flows, and enforce temporal legal versioning for historical reproducibility. Use when regulation texts change, legal references are updated, or compliance logic needs impact analysis."
argument-hint: "Provide previous and current regulation versions, affected articles/annexes, effective dates, and target modules for impact mapping"
user-invocable: true
disable-model-invocation: false
---

# CBAM Regulation Delta Tracker

## Purpose
This skill monitors CBAM legal changes and translates them into concrete system impact actions across calculation, validation, and reporting layers.

Primary outcomes:
- Detect article-level legal deltas between regulation versions
- Map each legal delta to impacted modules and workflows
- Enforce temporal legal logic so historical runs use period-correct regulation versions

## Scope
Applies to:
- EU CBAM regulation texts, annexes, implementing acts, and guidance updates
- Carbon math formulas and coefficients
- Data quality rule packs and threshold logic
- Explainability and reporting legal references
- Historical recalculation and audit replay workflows

## Mandatory Rules
1. Article-level delta extraction
- Regulation changes must be tracked at article/annex granularity.
- For each update, compute structured old-vs-new legal diff.
- Delta output must identify added, removed, modified clauses.

2. Explicit impact mapping
- Every legal delta must be mapped to specific system targets:
  - carbon-math modules
  - data-quality rules
  - reporting/explainability references
- No legal change is considered processed until impact mapping is complete.

3. Temporal legal versioning
- Legal references must be versioned with valid_from and valid_to boundaries.
- Historical calculations must bind to regulation version active on calculation period date.
- Backdated re-runs must not use current law by default.

## Legal Versioning Contract
Each legal artifact should include:
- legal_doc_id
- legal_version
- source_url_or_identifier
- publication_date
- effective_date
- valid_from
- valid_to (optional)
- supersedes (optional)
- status (draft, active, deprecated)

Each clause-level delta should include:
- delta_id
- legal_doc_id
- old_version
- new_version
- clause_reference (article/annex)
- change_type (ADDED, REMOVED, MODIFIED)
- old_text_hash
- new_text_hash
- semantic_change_summary

## When To Use
Use this skill when:
- New EU CBAM text or amendment is published
- Existing legal references are revised
- Carbon math or compliance rules need legal re-alignment
- Historical audits require period-correct legal replay
- Governance teams need legal change impact reports

Trigger words:
- regulation delta, legal diff, cbam amendment, impact analysis, temporal legal logic, versioned legal references

## Step-by-Step Procedure
1. Ingest regulation versions
- Register old and new legal texts with metadata and dates.
- Normalize clause identifiers (article/annex numbering).

2. Compute clause-level delta
- Compare old vs new content per clause.
- Classify each change as ADDED, REMOVED, or MODIFIED.

3. Perform semantic impact triage
- Mark change severity: low, medium, high.
- Identify if change affects calculations, validation, reporting, or disclosure language only.

4. Map to system components
- Link each delta to affected modules:
  - carbon-math-governance
  - data-quality-rule-engine
  - explainability-evidence-composer
  - payload mapping/reporting paths

5. Define remediation actions
- For each impacted target, define required code/config/docs updates.
- Assign owners, due dates, and release scope.

6. Apply temporal version policy
- Update legal version registry with validity window.
- Ensure calculation runners select legal version by reporting period.

7. Validate replay compatibility
- Re-run historical scenarios using period-correct legal version.
- Confirm no contamination from newer regulation versions.

8. Publish delta impact package
- Emit machine-readable delta file.
- Emit human-readable legal impact report for compliance stakeholders.

## Required Decision Points
1. Substantive vs editorial change
- Editorial-only changes may skip math/rule updates but still require trace entry.
- Substantive changes require full impact mapping and release gate checks.

2. Immediate vs scheduled activation
- If effective_date is future, queue activation with temporal boundary.
- If already effective, apply expedited compliance update workflow.

3. Multi-module conflict resolution
- If one legal delta impacts conflicting module behaviors, prioritize legally conservative interpretation and flag for legal review.

## Standard Impact Mapping Contract
Per delta item, required fields:
- delta_id
- clause_reference
- change_type
- impact_domain (math, rules, reporting, mixed)
- impacted_components[]
- impacted_metrics[]
- required_actions[]
- owner
- due_date
- risk_level
- legal_review_required

## Temporal Logic Rules
1. Version selection
- Select legal version where valid_from <= period_date < valid_to (or no valid_to).

2. Recalculation integrity
- Historical period reruns must lock to that period's legal version.
- Any override must be explicit, logged, and marked non-standard.

3. Explainability alignment
- Evidence reports must cite legal version active for the computed period, not latest by default.

## Compliance Failure Codes
Recommended codes:
- REGDELTA_VERSION_NOT_REGISTERED
- REGDELTA_CLAUSE_DIFF_MISSING
- REGDELTA_IMPACT_MAP_INCOMPLETE
- REGDELTA_TEMPORAL_BINDING_FAILED
- REGDELTA_HISTORICAL_REPLAY_MISMATCH
- REGDELTA_LEGAL_REFERENCE_STALE

Each failure should include:
- code
- delta_id or clause_reference
- affected_component
- period_date
- expected_legal_version
- actual_legal_version
- severity
- trace_id

## Quality Gates
A regulation delta cycle is complete only if all pass:
- Clause-level delta extraction complete
- Impact map covers all substantive changes
- Temporal legal version registry updated
- Historical replay checks pass for sampled periods
- Reporting references updated to correct legal versions
- Legal/compliance review sign-off recorded

## Anti-Patterns
- Tracking only document-level changes without article granularity
- Applying latest regulation to historical periods by default
- Updating formulas without legal clause linkage
- Closing legal delta without module impact mapping
- Mixing effective_date and publication_date semantics

## Example Prompt Starters
- "Use cbam-regulation-delta-tracker to compare old/new CBAM annexes and produce an impact map for math, rules, and reporting modules."
- "Apply cbam-regulation-delta-tracker to enforce temporal legal version selection for 2026 and 2027 historical reruns."
- "Use cbam-regulation-delta-tracker to generate a clause-level delta report with remediation actions and owners."

## Output Contract For This Skill
When invoked, this skill should produce:
- Clause-level legal delta summary
- System impact map across math, rules, and reporting
- Temporal version binding policy validation
- Actionable remediation plan with priorities
- Legal/compliance review checklist and release gates
