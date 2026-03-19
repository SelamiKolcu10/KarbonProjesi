---
name: scenario-simulation-playbook
description: "Standardize Strategist scenario generation with predefined playbook templates, enforce comparable CAPEX/OPEX/ROI reporting, and require invocation of financial-stress-sensitivity-analyzer for parameter stress validation. Use when producing management-ready scenario comparisons in CBAM workflows."
argument-hint: "Provide baseline payload, scenario families, template assumptions, capex/opex fields, and target comparison horizon"
user-invocable: true
disable-model-invocation: false
---

# Scenario Simulation Playbook

## Purpose
This skill enforces a centralized playbook for Strategist simulations so scenario outputs are consistent, reproducible, and comparable at management level.

Primary outcomes:
- Eliminate ad hoc personal scenario assumptions
- Enforce template-based scenario execution
- Produce comparable CAPEX vs OPEX and ROI outputs across scenarios

## Scope
Applies to:
- Strategist scenario design and execution
- Green Shift, Scrap Maximization, Process Efficiency, and future scenario families
- Investment decision reports for leadership
- Scenario comparison sections in executive outputs

## Mandatory Rules
1. Template-only scenario execution
- Every scenario run must use predefined scenario templates.
- Free-form personal assumptions are forbidden.
- Each template must define baseline, start/end parameters, and assumption boundaries.

2. Mandatory stress invocation
- For every scenario parameter set, financial-stress-sensitivity-analyzer must be invoked.
- Scenario output is invalid if stress/sensitivity validation is missing.
- Stress results must be attached to scenario comparison output.

3. Comparable management reporting
- Scenario comparison must include CAPEX, OPEX savings, ROI/payback, and risk markers.
- Reporting format must be normalized across all scenario families.
- Results must be ranked by consistent decision metrics.

## Dependency Contract
This skill depends on:
- financial-stress-sensitivity-analyzer (required)
- carbon-math-governance (formula authority)
- explainability-evidence-composer (optional for regulator-grade narrative)

If required dependency invocation is missing, mark run as non-compliant.

## Scenario Template Contract
Each scenario template should include:
- template_id
- template_version
- scenario_family
- objective
- baseline_requirements
- start_parameters
- end_parameters
- fixed_assumptions
- variable_parameters
- constraint_policy
- required_outputs
- governance_references

Recommended scenario families:
- GREEN_SHIFT
- SCRAP_MAXIMIZATION
- PROCESS_EFFICIENCY
- HYBRID_COMBINED

## Canonical Scenario Run Contract
Each run should include:
- run_id
- trace_id
- template_id
- template_version
- baseline_snapshot
- scenario_parameters
- stress_analysis_ref
- financial_outputs
- ranking_metrics
- generated_at

## When To Use
Use this skill when:
- Strategist needs to generate or compare mitigation strategies
- New scenario family is introduced
- Investment committee requires standardized business-case outputs
- Existing scenario logic is being audited for consistency

Trigger words:
- scenario playbook, strategist scenarios, capex opex comparison, roi, payback, strategy simulation, comparable report

## Step-by-Step Procedure
1. Select baseline and template set
- Load approved baseline payload.
- Select scenario templates from governed playbook only.

2. Validate template inputs
- Check required fields and parameter bounds.
- Reject incomplete or out-of-policy parameter sets.

3. Execute scenario simulations
- Run each template with governed deterministic formulas.
- Capture output metrics in canonical format.

4. Invoke stress analyzer (mandatory)
- Call financial-stress-sensitivity-analyzer for each scenario parameterization.
- Attach baseline/best/worst and sensitivity outputs to scenario run.

5. Compute investment economics
- Calculate CAPEX, annual OPEX savings, payback period, and ROI.
- Use consistent horizon and discount assumptions if defined by policy.

6. Build comparable report table
- Normalize all scenario outputs into one comparison schema.
- Rank scenarios by primary and secondary decision metrics.

7. Validate and publish
- Confirm dependency invocation evidence exists.
- Emit machine-readable and executive-readable reports.

## Investment and ROI Contract
Required financial fields per scenario:
- estimated_capex_eur
- annual_opex_savings_eur
- annual_tax_savings_eur
- total_annual_benefit_eur
- payback_period_years
- roi_percent
- risk_band

Recommended formulas:
- total_annual_benefit = annual_opex_savings + annual_tax_savings
- payback_years = capex / total_annual_benefit (if benefit > 0)
- annualized_capex_proxy = capex / analysis_horizon_years
- roi_percent = ((total_annual_benefit - annualized_capex_proxy) / annualized_capex_proxy) * 100

If governance policy defines alternate ROI formula, that policy is authoritative.

## Comparable Report Standard
A valid comparison report should include:
- baseline summary
- scenario-by-scenario assumption table
- stress/sensitivity summary per scenario
- CAPEX/OPEX/ROI matrix
- ranking by selected KPI set
- recommendation band (quick win, strategic, high risk)

Required sorting views:
- Highest annual benefit
- Fastest payback
- Lowest risk-adjusted exposure

## Required Decision Points
1. Template applicability
- If template prerequisites are missing, skip with explicit reason.
- Do not auto-invent missing parameters.

2. Stress result gating
- If stress analyzer returns non-compliant status, scenario cannot be recommended.

3. Ranking tie-break
- Define deterministic tie-break order (e.g., risk -> payback -> benefit).

4. Combined scenario handling
- Combined scenarios must disclose interaction assumptions and avoid double-counting savings.

## Compliance Failure Codes
Recommended codes:
- PLAYBOOK_TEMPLATE_NOT_FOUND
- PLAYBOOK_TEMPLATE_VERSION_UNSUPPORTED
- PLAYBOOK_REQUIRED_INPUT_MISSING
- PLAYBOOK_STRESS_INVOCATION_MISSING
- PLAYBOOK_NONCOMPARABLE_OUTPUT_SCHEMA
- PLAYBOOK_ROI_CALCULATION_INVALID

Each failure should include:
- code
- run_id
- template_id
- scenario_family
- message
- severity
- trace_id

## Quality Gates
A scenario playbook run is complete only if all pass:
- Approved template used for each scenario
- financial-stress-sensitivity-analyzer invocation recorded
- CAPEX/OPEX/ROI metrics computed in canonical schema
- Comparable report produced for all valid scenarios
- Ranking logic deterministic and documented
- No double-counting in combined scenarios

## Anti-Patterns
- Allowing analyst-specific one-off assumptions outside template
- Skipping stress/sensitivity validation step
- Comparing scenarios with different metric schemas
- Reporting ROI without clear formula and horizon
- Recommending scenarios with missing stress evidence

## Example Prompt Starters
- "Use scenario-simulation-playbook to run Green Shift, Scrap, and Efficiency templates and return a comparable CAPEX/OPEX/ROI table."
- "Apply scenario-simulation-playbook and invoke financial-stress-sensitivity-analyzer for each scenario before ranking recommendations."
- "Use scenario-simulation-playbook to produce a board-ready comparison with payback ranking and risk bands."

## Output Contract For This Skill
When invoked, this skill should produce:
- Template selection and applicability summary
- Scenario run outputs in canonical comparable schema
- Linked stress/sensitivity results per scenario
- CAPEX/OPEX/ROI ranking matrix
- Management recommendation summary with deterministic tie-break logic
