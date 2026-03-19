---
name: golden-baseline-regression
description: "Run deterministic regression checks with golden datasets to protect critical carbon emission and tax calculations. Use when formulas, coefficients, constants, or mapping logic change, and enforce CI/CD blocking on tolerance breaches with analytic diff reporting."
argument-hint: "Provide changed models/constants, golden dataset location, tolerance policy, and expected pass/fail gates"
user-invocable: true
disable-model-invocation: false
---

# Golden Baseline Regression

## Purpose
This skill guarantees numerical integrity for critical carbon emissions and tax outputs by comparing current results against approved golden datasets.

Primary outcomes:
- Detect unintended numerical drift after math or coefficient updates
- Enforce fail-fast CI/CD blocking when tolerance is exceeded
- Produce clear analytic diff reports for investigation and rollback decisions

## Scope
Applies to all high-impact outputs, including:
- Total emissions (tCO2e)
- Scope-level emissions (Scope 1/2/process/precursor)
- Effective tax liability (EUR)
- Per-ton liability and key derived metrics
- Any governed result used by Auditor, Strategist, or executive reports

## Mandatory Rules
1. Golden comparison after every math update
- Any change to formulas, coefficients, constants, mapping, or rounding policy MUST trigger golden regression.
- No math-related change is considered valid without baseline comparison.

2. Strict tolerance-based blocking
- If absolute or relative difference exceeds policy tolerance, the pipeline MUST fail immediately.
- No manual bypass in default CI/CD path.
- Failure must include machine-readable error code and failing metric list.

3. Analytic diff reporting on failure
- For every failed case, report old vs new values and exact deltas.
- Diff report must include per-metric and per-test-case breakdown.
- Report must be archived as build artifact for auditability.

## Golden Dataset Contract
Each dataset entry should include at minimum:
- test_case_id
- input_payload
- expected_outputs
- expected_version (optional but recommended)
- legal_or_business_context (optional)
- tolerance_profile_id

Expected outputs should include explicit numeric fields, e.g.:
- total_emissions_tco2e
- effective_liability_eur
- scope_1_direct_tco2e
- scope_2_indirect_tco2e

## Tolerance Policy
Define tolerance centrally and version it.

Recommended structure:
- absolute_tolerance per metric
- relative_tolerance per metric
- optional floor thresholds for near-zero stability

Evaluation rule per metric:
- Pass if abs(new - golden) <= abs_tol
- OR pass if abs(new - golden) / max(abs(golden), floor) <= rel_tol
- Else fail

Do not use implicit tolerance. Every compared metric must have explicit policy.

## When To Use
Use this skill when:
- Emission factors are updated
- Carbon tax formula or phase-in coefficient changes
- Mapping/canonicalization logic changes numeric outputs
- Decimal/rounding behavior changes
- Refactoring modifies calculation sequence

Trigger words:
- regression, golden dataset, tolerance, numerical drift, baseline test, ci blocking, diff report

## Step-by-Step Procedure
1. Identify change set
- List touched formulas/constants/modules.
- Tag impacted output metrics.

2. Select relevant golden suite
- Choose full suite for broad math changes.
- Choose targeted suite for localized changes.
- Ensure dataset version matches governance policy.

3. Execute deterministic regression run
- Run with fixed configuration and deterministic runtime.
- Capture raw outputs per test case.

4. Compare against golden baseline
- Apply central tolerance policy by metric.
- Mark pass/fail per metric and per test case.

5. Enforce CI gate
- If any fail exists, return non-zero status and block pipeline.
- Emit standardized failure summary.

6. Generate analytic diff report
- Include old value, new value, absolute delta, relative delta, tolerance used, pass/fail.
- Include top failing metrics ranked by normalized deviation.

7. Publish artifacts
- Save structured JSON report.
- Save human-readable summary for reviewers.
- Attach to CI job outputs.

## Decision Points
1. Full vs targeted regression
- If constants/formulas changed globally: run full suite.
- If change is localized and proven isolated: targeted suite allowed, but at least one cross-system sanity case required.

2. Tolerance profile selection
- Use default strict profile for financial and tax metrics.
- Use metric-specific profile only if documented and approved.

3. Baseline update eligibility
- Golden baseline can be updated only after explicit approval.
- Baseline update PR must include legal/math rationale and reviewer sign-off.

## Failure Error Contract
Recommended error codes:
- REGRESSION_TOLERANCE_EXCEEDED
- REGRESSION_GOLDEN_DATASET_MISSING
- REGRESSION_METRIC_NOT_COMPARABLE
- REGRESSION_POLICY_NOT_DEFINED
- REGRESSION_DETERMINISM_VIOLATION

Each failure should include:
- code
- test_case_id
- metric_name
- golden_value
- current_value
- absolute_delta
- relative_delta
- abs_tolerance
- rel_tolerance
- trace_id

## Diff Report Contract
A valid analytic diff report must include:
- run_id and commit_sha
- dataset_version and policy_version
- overall status (PASS/FAIL)
- total_cases, passed_cases, failed_cases
- per-case metric table
- top deviations summary
- blocker reason list

Recommended report sections:
1. Executive summary
2. Failing test cases
3. Metric-level deltas
4. Suggested investigation path

## Quality Gates
A regression workflow is complete only if all pass:
- Golden dataset integrity check passed
- Deterministic rerun consistency check passed
- Tolerance policy resolved for all metrics
- CI gate behavior verified (fail on breach)
- Diff report generated and archived

## Anti-Patterns
- Updating baseline to hide regression without root-cause analysis
- Using one global loose tolerance for all metrics
- Ignoring relative drift near low absolute values
- Running regression without deterministic runtime controls
- Reporting only pass/fail without numeric deltas

## Example Prompt Starters
- "Use golden-baseline-regression to validate this coefficient update against golden datasets and block on tolerance breaches."
- "Apply golden-baseline-regression to generate a full analytic diff report for failing emissions and liability metrics."
- "Use golden-baseline-regression to define strict metric-level tolerances for CI gating."

## Output Contract For This Skill
When invoked, this skill should produce:
- Regression run plan (full/targeted)
- Metric tolerance map and policy validation
- Pass/fail gate decision for CI/CD
- Structured analytic diff report blueprint
- Baseline update decision guidance with approval requirements
