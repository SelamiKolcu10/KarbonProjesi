---
name: carbon-math-governance
description: "Govern emission factors, carbon tax formulas, and CBAM coefficients from a single deterministic source of truth for Auditor and Strategist agents. Use when updating regulatory constants, enforcing deterministic calculations, preventing formula drift, and implementing Decimal-safe financial math."
argument-hint: "Describe affected formulas/constants, legal references, current values, desired changes, and precision requirements"
user-invocable: true
disable-model-invocation: false
---

# Carbon Math Governance

## Purpose
This skill enforces a single, regulation-aligned, deterministic governance model for all carbon math used by Auditor and Strategist agents.

Primary outcomes:
- Centralize approved emission factors and CBAM coefficients
- Prevent formula drift across agents and modules
- Guarantee deterministic outputs for same inputs
- Enforce precision-safe financial calculations with Decimal

## Scope
Applies to:
- Emission factors (fuel, electricity, process, precursor)
- Carbon tax and liability formulas
- CBAM phase-in coefficients and allocation parameters
- Financial projections and stress-test calculations
- Any shared constants used by Auditor and Strategist

## Mandatory Rules
1. Approved reference math only
- Agents must never invent formulas, coefficients, or phase factors.
- Only legally approved or governance-approved constants are allowed.
- Every formula and constant must include legal/reference provenance.

2. Full determinism
- Same input payload must always produce bitwise-equivalent logical results.
- No randomness, implicit time dependency, or hidden external state in core math.
- Ordering-sensitive operations must be explicitly stabilized.

3. Precision-safe financial arithmetic
- Use Decimal for tax/liability and monetary calculations.
- Avoid binary floating arithmetic in financial paths.
- Rounding rules must be explicit, centralized, and test-covered.

## Canonical Governance Model
A governed math artifact must include:
- formula_id
- formula_expression
- legal_reference
- version
- effective_date
- replaced_by (optional)
- coefficient_set_id
- precision_policy_id

A governed coefficient must include:
- coefficient_name
- value
- unit
- source_reference
- valid_from
- valid_to (optional)
- approval_status

## When To Use
Use this skill when:
- Updating ETS price logic, CBAM phase-in schedule, or allocation rates
- Adding/changing emission factors in Auditor
- Running Strategist simulations dependent on governed constants
- Refactoring financial computation paths to Decimal
- Reviewing PRs that touch formulas/constants/math utilities

Trigger words:
- carbon math, formula governance, deterministic calculation, decimal precision, cbam factor, emission factor, liability math

## Step-by-Step Procedure
1. Identify affected math surface
- List all touched formulas and constants.
- Map producer modules and consumer modules.

2. Validate legal provenance
- Attach regulation reference for each formula/constant.
- Reject any value without verifiable source.

3. Apply versioned change policy
- Classify change: patch/minor/major governance update.
- Record old value, new value, rationale, and effective date.

4. Enforce Decimal in financial path
- Convert monetary and tax operations to Decimal.
- Define quantization and rounding mode centrally.
- Ban mixed float + Decimal operations.

5. Validate deterministic execution
- Remove nondeterministic dependencies.
- Ensure stable operation ordering and explicit rounding boundaries.

6. Cross-agent consistency check
- Confirm Auditor and Strategist consume same governed constants.
- Confirm no duplicated shadow constants in local modules.

7. Run governance quality gates
- Golden baseline tests pass.
- Determinism replay tests pass.
- Precision drift tests pass.
- Changelog and governance registry updated.

## Determinism Ruleset
1. Forbidden in core math:
- Randomized behavior
- Time-now driven coefficients
- Environment-dependent branching
- Unordered iteration that affects numeric output

2. Required in core math:
- Explicit function inputs
- Stable coefficient lookup by version/date
- Explicit rounding checkpoints
- Replayable execution with trace id and formula version

## Precision Policy
Use Decimal for:
- ETS price multiplication
- Net liable emissions cost
- Effective liability
- Scenario financial outputs
- Any monetary aggregation

Recommended policy:
- Parse input numeric strings into Decimal
- Keep internal arithmetic in Decimal
- Quantize only at defined output boundaries
- Record rounding mode and quantization in audit trail

Example baseline precision choices:
- Emission intensity: quantize to 0.0001
- Liability EUR: quantize to 0.01
- Coefficients: store as canonical string form for reproducibility

## Structured Governance Errors
Recommended codes:
- MATH_FORMULA_UNAPPROVED
- MATH_COEFFICIENT_UNAPPROVED
- MATH_REFERENCE_MISSING
- MATH_NONDETERMINISTIC_PATH
- MATH_DECIMAL_POLICY_VIOLATION
- MATH_PRECISION_DRIFT_DETECTED

Each error should include:
- code
- message
- formula_id or coefficient_name
- current_version
- trace_id
- severity

## Quality Gates
A math change is complete only if all pass:
- Formula and coefficient provenance verified
- Versioned governance record updated
- Decimal policy compliance validated
- Determinism replay test passes on repeated runs
- Regression baselines for emissions and tax pass
- Auditor and Strategist cross-consistency checks pass

## Anti-Patterns
- Duplicating constants in multiple modules
- Using float for liability math
- Implicitly changing formula semantics without version bump
- Backfilling missing coefficients with guessed values
- Applying hidden rounding at intermediate unknown steps

## Example Prompt Starters
- "Use carbon-math-governance to review this coefficient update for legal provenance, determinism, and Decimal precision compliance."
- "Apply carbon-math-governance to migrate tax liability math from float to Decimal with explicit quantization policy."
- "Use carbon-math-governance to validate Auditor and Strategist are consuming the same CBAM phase-in coefficients."

## Output Contract For This Skill
When invoked, this skill should produce:
- Impact summary of formula/coefficient changes
- Legal provenance validation result
- Determinism and precision compliance assessment
- Decimal migration checklist for affected calculations
- Regression and replay test plan with acceptance criteria
