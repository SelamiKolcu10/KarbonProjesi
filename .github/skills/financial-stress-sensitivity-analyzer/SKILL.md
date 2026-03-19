---
name: financial-stress-sensitivity-analyzer
description: "Run structured ETS-price, allocation, and CBAM phase-in stress and sensitivity analysis for Strategist using governed deterministic math. Use when evaluating baseline/best/worst financial exposure, tsunami-risk projections, and parameter impact ranking for decision support."
argument-hint: "Provide baseline assumptions, stress parameter ranges, time horizon, and target financial metrics for sensitivity scoring"
user-invocable: true
disable-model-invocation: false
---

# Financial Stress and Sensitivity Analyzer

## Purpose
This skill defines a strict framework for Strategist-side financial stress testing and sensitivity analysis over ETS price, allocation, and phase-in parameters.

Primary outcomes:
- Build a deterministic scenario matrix for financial risk forecasting
- Produce baseline, best-case, and worst-case exposure outputs
- Quantify which parameter drives the largest financial impact

## Scope
Applies to:
- ETS price shock simulations
- Allocation and phase-in variation analysis
- Multi-year CBAM liability projections (tsunami effect)
- Strategist recommendation prioritization based on financial risk

## Mandatory Rules
1. Matrix-based stress simulation standard
- Parameter shocks must be evaluated through explicit scenario matrices.
- Single-point narrative assumptions are insufficient.
- Matrix must support defined ranges (e.g., ETS +50%, allocation -20%).

2. Governed deterministic math only
- Simulation formulas MUST be sourced from carbon-math-governance.
- No ad hoc formula invention is allowed.
- All outputs must be reproducible with same inputs.

3. Quantified sensitivity reporting
- Report parameter impact on financial outputs mathematically.
- Include sensitivity weight/elasticity/correlation measures.
- Ranking must be data-driven, not qualitative guesswork.

## Dependency Contract
This skill depends on:
- carbon-math-governance (formula and coefficient authority)
- golden-baseline-regression (optional validation for changed stress logic)
- explainability-evidence-composer (optional regulator-grade narrative)

If carbon-math-governance references are missing, simulation is non-compliant.

## Canonical Scenario Model
Each scenario should include:
- scenario_id
- scenario_label (Baseline, Best-Case, Worst-Case, Custom)
- parameter_set
- formula_version_refs
- projection_horizon
- output_metrics
- generated_at
- trace_id

Parameter set should include at minimum:
- ets_price_eur_per_ton
- cbam_allocation_rate
- cbam_phase_factor
- optional volatility assumptions

## Stress Matrix Standard
Build matrix dimensions from governed parameters:
- ETS price levels (e.g., -20%, base, +30%, +50%)
- Allocation levels (e.g., base, conservative, aggressive)
- Phase-in levels (e.g., legal schedule variants by year)

Required matrix rules:
- Include at least 1 baseline scenario
- Include at least 1 favorable and 1 adverse scenario
- Keep parameter changes explicit and versioned

## Baseline/Best/Worst Definition
1. Baseline
- Uses approved current parameter values from governance registry.

2. Best-Case
- Uses favorable but policy-valid conditions (e.g., lower ETS, better allocation if allowed).

3. Worst-Case
- Uses adverse but realistic stress assumptions (e.g., ETS shock + tightened allocation).

No scenario can violate regulatory or governance constraints silently.

## When To Use
Use this skill when:
- Evaluating exposure under ETS volatility
- Preparing management risk briefings
- Comparing strategic options under uncertainty
- Updating phase-in assumptions over multi-year horizon
- Prioritizing investments by financial risk reduction effect

Trigger words:
- stress test, sensitivity, ets shock, tsunami effect, best case, worst case, risk matrix, financial exposure

## Step-by-Step Procedure
1. Define baseline and objective
- Select baseline payload and governed formula set.
- Define target outputs (effective liability, per-ton cost, 5-year exposure).

2. Configure stress matrix
- Declare parameter ranges and step sizes.
- Bind each axis to governed coefficients only.

3. Execute deterministic simulations
- Run all matrix scenarios with fixed deterministic configuration.
- Capture outputs and metadata per scenario.

4. Generate scenario tiers
- Extract baseline, best-case, worst-case from matrix results.
- Record assumptions and validity checks.

5. Compute sensitivity metrics
- Calculate parameter impact weights using defined math methods.
- Rank parameters by absolute and normalized effect size.

6. Produce management report
- Summarize exposure bands and top risk drivers.
- Flag threshold breaches and mitigation priorities.

7. Validate and archive
- Validate formula references and reproducibility.
- Save machine-readable results and human-readable summary.

## Sensitivity Analysis Contract
Required outputs per parameter:
- parameter_name
- local_sensitivity (partial effect near baseline)
- global_effect_range (min/max impact across matrix)
- normalized_weight (0-1 or percentage)
- rank
- confidence_note (if assumptions limit reliability)

Recommended methods:
- One-factor-at-a-time elasticity around baseline
- Finite-difference sensitivity on governed equations
- Scenario correlation to target metric (with caveat notes)

## Reporting Contract
A valid report should include:
- run_id and trace_id
- baseline assumptions
- scenario matrix definition
- baseline/best/worst summary
- sensitivity ranking table
- tsunami-effect projection summary (multi-year growth factor)
- mitigation recommendations aligned with top drivers

## Quality Gates
A stress/sensitivity workflow is complete only if all pass:
- All formulas resolved via carbon-math-governance
- Baseline/best/worst scenarios generated and reproducible
- Sensitivity ranking computed mathematically
- No non-governed parameter used
- Report includes assumptions, limits, and trace metadata

## Compliance Failure Codes
Recommended codes:
- STRESS_GOVERNED_FORMULA_MISSING
- STRESS_PARAMETER_OUT_OF_POLICY
- STRESS_SCENARIO_MATRIX_INCOMPLETE
- STRESS_NONDETERMINISTIC_OUTPUT
- STRESS_SENSITIVITY_CALCULATION_FAILED
- STRESS_BASELINE_REFERENCE_MISSING

Each failure should include:
- code
- scenario_id
- parameter_name (if applicable)
- expected_reference
- actual_reference
- severity
- trace_id

## Anti-Patterns
- Manually tweaking outputs without matrix execution
- Using custom math that bypasses carbon-math-governance
- Presenting best/worst scenarios without baseline anchor
- Reporting sensitivity ranking without numeric method disclosure
- Ignoring parameter policy constraints in stress setup

## Example Prompt Starters
- "Use financial-stress-sensitivity-analyzer to run ETS +50% stress matrix and produce baseline/best/worst liability outputs."
- "Apply financial-stress-sensitivity-analyzer to rank ETS, allocation, and phase-in parameters by normalized financial impact."
- "Use financial-stress-sensitivity-analyzer to prepare a tsunami-effect board report with 5-year exposure bands and top risk drivers."

## Output Contract For This Skill
When invoked, this skill should produce:
- Parameterized stress matrix specification
- Baseline/Best-Case/Worst-Case scenario outputs
- Sensitivity ranking and driver-weight report
- Assumption and governance-reference checklist
- Management decision summary with prioritized risk levers
