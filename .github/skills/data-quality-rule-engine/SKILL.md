---
name: data-quality-rule-engine
description: "Define and enforce centralized business-logic and physics validation rules for incoming raw data. Use when blocking impossible values, isolating rule governance from orchestration code, and producing versioned violation reports in CBAM workflows."
argument-hint: "Provide input schema, sector/regulation context, required validation rules, and expected violation report format"
user-invocable: true
disable-model-invocation: false
---

# Data Quality Rule Engine

## Purpose
This skill establishes a centralized validation engine that checks all incoming raw data against business logic and physical plausibility before orchestration proceeds.

Primary outcomes:
- Detect and block impossible or illogical inputs early
- Decouple rule governance from orchestration runtime code
- Emit standardized, versioned violation reports for audit and operations

## Scope
Applies to:
- Data Miner output payloads
- Mapped payloads before Auditor ingestion
- Manual/API-submitted payloads entering orchestrator workflows
- Sector-specific rule packs and regulation-driven constraints

## Mandatory Rules
1. Hard blocking for impossible/illogical data
- Negative consumption, impossible ranges, and physical inconsistencies must be rejected.
- Capacity and threshold violations must fail validation when policy marks them as blocking.
- No silent correction for critical rule breaches.

2. Full rule-engine isolation from orchestration code
- Validation rules must be managed in the rule engine boundary, not embedded in orchestration flow logic.
- New regulation or sector constraints must be added through rule definitions/configuration.
- Orchestrator should call engine APIs only, without hardcoded per-rule branches.

3. Standardized, versioned violation reporting
- Every violation report must identify rule_id and rule_version.
- Report must include reason, offending value, expected bounds, and severity.
- Error payload must be machine-readable and reproducible.

## Rule Engine Governance Model
Each rule definition should include:
- rule_id
- rule_version
- rule_name
- category (physics, business, regulatory, consistency)
- target_fields
- condition_expression
- threshold_config
- severity (INFO, WARNING, ERROR, CRITICAL)
- blocking (true/false)
- enabled (true/false)
- valid_from
- valid_to (optional)
- source_reference (regulation/industry source)

## Validation Categories
1. Physics rules
- Non-negative and non-zero constraints where applicable
- Energy intensity plausible ranges
- Production-energy consistency checks
- Capacity upper-bound checks

2. Business-logic rules
- Required field completeness
- Cross-field consistency (period, facility, allocation)
- Contract-level semantic validations

3. Regulatory rules
- Sector/regulation-specific thresholds
- Reporting period constraints
- Allocation coefficient boundaries

4. Consistency rules
- Unit-state consistency after canonicalization
- Duplicate/conflicting source value checks
- Time-series monotonic or bounded checks (if required)

## When To Use
Use this skill when:
- Adding or updating data quality checks for incoming payloads
- Enforcing strict fail-fast validation in ingestion/orchestration
- Migrating scattered validation logic into centralized rule packs
- Rolling out new sector/regulation requirements without orchestration edits
- Investigating repeated quality failures and false positives

Trigger words:
- data quality, validation engine, physics checks, business logic rules, rule versioning, fail-fast, violation report

## Step-by-Step Procedure
1. Define validation surface
- List payload entry points and target schemas.
- Identify required fields and critical physical constraints.

2. Author rule set
- Create explicit rules with rule_id and rule_version.
- Assign category, severity, blocking policy, and threshold parameters.

3. Externalize rule definitions
- Keep rule configuration outside orchestration decision code.
- Bind orchestrator to rule engine interface only.

4. Execute rule evaluation
- Evaluate all enabled rules deterministically.
- Collect pass/fail and per-rule evidence.

5. Apply decision policy
- If any blocking rule fails, reject payload immediately.
- If non-blocking warnings exist, allow flow with warning report.

6. Emit standardized report
- Create machine-readable violation report with versioned rule metadata.
- Include concise human-readable summary for operators.

7. Validate maintainability
- Confirm new rules can be added/updated without orchestrator code changes.
- Confirm rule pack versioning and changelog traceability.

## Required Decision Points
1. Blocking vs warning
- CRITICAL and ERROR physics violations should default to blocking.
- WARNING should not block unless explicitly configured by policy.

2. Rule precedence
- If multiple rules fail, report all violations but prioritize blocking-first summary.
- Do not short-circuit silently; preserve full failure context.

3. Rule lifecycle
- New rule: increment rule set version and publish release note.
- Rule modification: bump rule_version and record rationale.
- Rule deprecation: keep historical compatibility for audit replay.

## Standard Violation Report Contract
Required fields:
- report_id
- trace_id
- payload_id
- engine_version
- ruleset_version
- overall_status (PASS, WARN, FAIL)
- blocking_violation_count
- warning_count
- evaluated_at
- violations[]

Each violation item must include:
- rule_id
- rule_version
- category
- severity
- blocking
- target_field
- offending_value
- expected_condition
- message
- source_reference

## Recommended Error Codes
- DQ_NEGATIVE_VALUE
- DQ_PHYSICS_IMPOSSIBLE_INTENSITY
- DQ_CAPACITY_LIMIT_EXCEEDED
- DQ_REQUIRED_FIELD_MISSING
- DQ_ALLOCATION_OUT_OF_RANGE
- DQ_CROSS_FIELD_INCONSISTENT
- DQ_RULE_ENGINE_CONFIG_INVALID

## Quality Gates
A rule-engine change is complete only if all pass:
- New/updated rules have explicit versioning
- Blocking policy is declared for each rule
- Violation report schema validation passes
- At least one pass and one fail test per new blocking rule
- Orchestrator path unchanged for rule additions
- Historical replay tests pass for prior ruleset versions

## Anti-Patterns
- Hardcoding rule logic directly inside orchestrator handlers
- Returning generic errors without rule_id/rule_version
- Auto-correcting critical invalid data without audit trace
- Updating thresholds without ruleset version bump
- Failing on first rule and hiding other relevant violations

## Example Prompt Starters
- "Use data-quality-rule-engine to define blocking physics rules for energy-production consistency and emit versioned violation reports."
- "Apply data-quality-rule-engine to move validation logic from orchestrator code into externalized ruleset configuration."
- "Use data-quality-rule-engine to add a new sector threshold rule without changing orchestration flow logic."

## Output Contract For This Skill
When invoked, this skill should produce:
- Rule inventory and categorization map
- Blocking/warning decision policy
- Versioned violation report schema
- Rule lifecycle and governance checklist
- Regression test plan for rule behavior and orchestrator isolation
