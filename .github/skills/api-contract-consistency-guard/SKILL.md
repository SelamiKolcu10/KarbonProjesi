---
name: api-contract-consistency-guard
description: "Continuously compare root API and modular API endpoint/response contracts, cross-reference them with internal agent contracts, and block unversioned breaking changes in CI/CD with integrator-focused endpoint delta reports. Use when protecting frontend/external integrations from API drift."
argument-hint: "Provide API specs or Pydantic models, baseline version, target version, and CI/CD break-policy requirements"
user-invocable: true
disable-model-invocation: false
---

# API Contract Consistency Guard

## Purpose
This skill enforces strict API contract consistency between root and modular API surfaces, prevents unversioned breaking changes, and protects frontend/external integrators from drift.

Primary outcomes:
- Continuous cross-check of endpoint/request/response contracts
- Hard CI/CD blocking for backward-incompatible, unversioned API changes
- Actionable endpoint-level delta reports for integrator impact

## Scope
Applies to:
- Root API surface (top-level API entrypoints)
- Modular API surface (versioned or submodule API entrypoints)
- OpenAPI/Swagger and Pydantic-based schema definitions
- Frontend and external integrator payload expectations
- Agent-facing contracts linked via agent-contract-registry

## Mandatory Rules
1. Continuous cross-reference validation
- All API request/response schemas must be cross-checked against internal agent contracts from agent-contract-registry.
- API-level and agent-level contract drift must be detected automatically.
- Contract checks must run in CI and pre-release validation.

2. Strict backward-compatibility gate
- Any breaking API change (field removal, rename, type narrowing, requiredness increase) is blocked unless version bump policy is satisfied.
- Unversioned breaking change is always CI fail.
- Version bump must align with change class (e.g., v1 -> v2 for breaking changes).

3. Integrator-focused delta reporting
- On detected drift, generate endpoint-level delta report for frontend and external consumers.
- Report must include changed paths, methods, request/response field deltas, and impact severity.
- Report must be machine-readable and human-readable.

## Dependency Contract
This skill depends on:
- agent-contract-registry (source of truth for internal contract governance)
- agent-messaging-error-taxonomy (optional standardized failure codes)
- cbam-regulation-delta-tracker (optional legal-triggered API impact linkage)

If internal contract baseline is missing, consistency result is non-compliant.

## Canonical API Contract Artifact
Each API contract snapshot should include:
- api_surface_id (root/modular)
- api_version
- generated_at
- source_ref (openapi path or model package)
- endpoint_catalog
- schema_catalog
- hash_signature

Each endpoint entry should include:
- path
- method
- operation_id
- request_schema_ref
- response_schema_refs
- auth_profile (optional)
- deprecation_status

## Breaking Change Definition
Classify as breaking by default when any of these occur without version bump:
- Endpoint removed
- Path or method changed incompatibly
- Request field removed/renamed
- Response field removed/renamed
- Field type narrowed (e.g., number -> integer)
- Optional field becomes required
- Enum removes previously valid value

Non-breaking examples:
- New optional response field
- New endpoint in same version (if no contract conflict)
- Extended enum with backward-compatible consumer behavior

## When To Use
Use this skill when:
- API contracts are changed or refactored
- Root and modular APIs diverge over time
- Frontend integration instability is suspected
- Release pipelines need strict compatibility gates
- Team needs explicit API drift auditing

Trigger words:
- api contract drift, openapi diff, pydantic schema compare, backward compatibility gate, breaking change block, endpoint delta

## Step-by-Step Procedure
1. Collect contract sources
- Load root API schema (OpenAPI/Pydantic snapshot).
- Load modular API schema (OpenAPI/Pydantic snapshot).
- Load internal contract references from agent-contract-registry.

2. Normalize and align schemas
- Normalize endpoint identifiers and model references.
- Resolve alias/name mapping and version metadata.

3. Run cross-reference checks
- Compare root vs modular endpoint signatures.
- Compare API payload models vs internal agent contracts.
- Flag drift by endpoint/method/field.

4. Classify diffs
- Mark each diff as breaking/non-breaking.
- Determine required version bump from policy.

5. Enforce CI compatibility gate
- If breaking and version bump missing: hard fail CI.
- If non-breaking: pass with informational notices.

6. Generate delta report
- Produce endpoint-level diff artifacts for frontend/external integrators.
- Include impact severity and migration hints.

7. Publish governance outputs
- Save machine-readable diff JSON.
- Save review summary for release decision.

## Required Decision Points
1. Version bump requirement
- Breaking change + no major bump -> block
- Breaking change + valid bump -> allow with migration notes

2. Alias/deprecation handling
- Temporary aliases may downgrade severity if compatibility remains.
- Deprecated fields must include removal timeline.

3. Integrator impact severity
- High: payload incompatibility or endpoint removal
- Medium: response semantic change or enum contraction risk
- Low: additive optional fields

## CI/CD Enforcement Contract
Required gate outcomes:
- PASS: no breaking changes or valid versioned breaking transition
- WARN: non-breaking drifts requiring docs update
- FAIL: unversioned breaking drift detected

On FAIL, required outputs:
- failing_endpoints list
- breaking_fields list
- expected_version_bump
- suggested_migration_actions

## Delta Report Contract
Report must include:
- report_id
- baseline_version
- candidate_version
- generated_at
- overall_status
- endpoint_deltas[]
- schema_deltas[]
- integrator_impact_summary
- frontend_action_items
- external_integrator_action_items

Each endpoint delta item should include:
- path
- method
- change_type (ADDED, REMOVED, MODIFIED)
- request_changes
- response_changes
- breaking (true/false)
- severity
- migration_note

## Compliance Failure Codes
Recommended codes:
- API_CONTRACT_BASELINE_MISSING
- API_CONTRACT_CROSSREF_FAILED
- API_BREAKING_CHANGE_UNVERSIONED
- API_SCHEMA_DRIFT_DETECTED
- API_ENDPOINT_SIGNATURE_MISMATCH
- API_DELTA_REPORT_GENERATION_FAILED

Each failure should include:
- code
- endpoint_or_schema_ref
- detected_change
- required_action
- severity
- trace_id

## Quality Gates
An API consistency run is complete only if all pass:
- Root and modular API specs successfully parsed
- Internal contract cross-reference completed
- Breaking vs non-breaking classification validated
- CI gate decision produced deterministically
- Endpoint delta report generated for integrators
- Versioning/migration notes recorded

## Anti-Patterns
- Comparing only endpoint names without request/response schema checks
- Allowing breaking payload changes under same API version
- Skipping cross-reference with internal agent contracts
- Shipping drift without frontend/integrator delta report
- Manual exception handling without traceable policy record

## Example Prompt Starters
- "Use api-contract-consistency-guard to compare root and modular OpenAPI specs and block unversioned breaking changes in CI."
- "Apply api-contract-consistency-guard to cross-reference Pydantic API models with agent-contract-registry and produce frontend delta report."
- "Use api-contract-consistency-guard to classify endpoint changes by severity and required version bump."

## Output Contract For This Skill
When invoked, this skill should produce:
- Root vs modular API consistency assessment
- Internal contract cross-reference findings
- CI gate decision with breaking-change policy checks
- Integrator-focused endpoint delta report
- Version bump and migration action recommendations
