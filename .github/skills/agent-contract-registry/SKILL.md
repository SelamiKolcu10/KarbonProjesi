---
name: agent-contract-registry
description: "Manage cross-agent JSON and Pydantic contracts for Data Miner, Auditor, and Strategist. Use when defining message schemas, preventing schema drift, versioning models, validating required fields, and enforcing backward compatibility in CBAM workflows."
argument-hint: "Describe the contract change, affected agent interfaces, current version, and expected compatibility behavior"
user-invocable: true
disable-model-invocation: false
---

# Agent Contract Registry

## Purpose
This skill enforces stable, testable, and versioned data contracts between Data Miner, Auditor, and Strategist agents.

Primary objectives:
- Prevent schema drift across agent boundaries
- Ensure all inter-agent payloads are strongly validated
- Keep backward compatibility as a default policy
- Provide explicit version evolution and deprecation rules

## When To Use
Use this skill when:
- Adding or changing fields in shared payloads
- Introducing new output models from Data Miner
- Updating Auditor input or Strategist report contracts
- Migrating API responses that mirror internal agent contracts
- Reviewing pull requests that touch models, mappers, or orchestration I/O

Typical trigger words:
- contract, schema, versioning, required fields, compatibility, payload, pydantic, json schema, migration, drift

## Mandatory Rules
1. Strict schema validation for all inter-agent communication
- Every payload MUST be represented by a concrete Pydantic model.
- Every payload MUST produce a machine-readable JSON Schema.
- Dict-only ad hoc payloads are not allowed at integration boundaries.

2. Explicit versioning and required fields
- Every shared model MUST expose an explicit contract version, for example model_version.
- Required fields MUST be clearly defined and enforced in the schema.
- Optional fields MUST have clear defaults and semantic meaning.

3. Backward compatibility by default
- Existing consumers MUST continue working after contract changes.
- Additive changes are preferred over breaking changes.
- Field removal or rename requires a deprecation cycle and migration path.

## Scope
This skill covers these boundaries:
- Data Miner output -> Pipeline mapper input
- Pipeline mapped payload -> Auditor input
- Auditor output -> Strategist input
- Strategist output -> Orchestrator/API response contracts

## Procedure
1. Identify the contract surface
- List producer agent, consumer agent, and transport format.
- Record current model names, versions, and required fields.

2. Classify the change type
- Additive: new optional field, new enum member with safe default handling.
- Behavioral: same fields, changed semantics or validation constraints.
- Breaking: removed field, renamed field, type narrowing, requiredness increase.

3. Apply versioning policy
- Patch: non-breaking metadata/documentation updates.
- Minor: additive backward-compatible schema updates.
- Major: breaking changes that require migration.

4. Update models and schema artifacts
- Update Pydantic models first.
- Regenerate or validate JSON Schema output.
- Ensure required fields and defaults are accurate.

5. Add compatibility adapters
- Provide mapping logic for old and new versions where needed.
- Accept legacy aliases during deprecation windows.
- Emit warnings for deprecated fields without hard-failing immediately.

6. Validate contract integrity
- Run unit and integration tests for producer and consumer sides.
- Add regression tests for at least one previous contract version.
- Verify orchestrator flow end-to-end with representative payloads.

7. Publish contract changelog
- Document what changed, why, impact, and migration guidance.
- Mark deprecation start date and planned removal version.

## Decision Matrix
- If change is additive and optional: allow in current major version.
- If change alters meaning but not shape: require semantic release note and targeted tests.
- If change is breaking: block merge unless migration adapters and rollout plan exist.

## Quality Gates
A contract change is complete only if all are true:
- Producer and consumer models compile and validate
- JSON Schema reflects actual runtime validators
- Required fields are explicit and covered by tests
- Backward compatibility tests pass for previous supported version
- Changelog includes migration guidance

## Backward Compatibility Policy
- Support at least one previous minor version at minimum.
- Use a deprecation period before removing fields.
- Never silently reinterpret field meaning.
- Prefer new fields over changing old field semantics.

## Suggested PR Checklist
- Contract boundary identified
- Version bump justified
- Required fields reviewed
- Defaults reviewed for optional fields
- Legacy payload compatibility verified
- Integration tests updated
- Changelog updated

## Failure Modes To Detect Early
- Hidden required field introduced accidentally
- Enum tightening that rejects old payloads
- Precision/type changes that alter financial calculations
- Mapper drift between extraction output and audit input
- API response shape diverging from strategist report model

## Example Prompt Starters
- "Apply agent-contract-registry to add a new optional precursor field without breaking Auditor compatibility."
- "Use agent-contract-registry to review this PR for schema drift risks between Data Miner and Auditor."
- "Use agent-contract-registry to design a major version migration plan for Strategist report contract changes."

## Output Contract For This Skill
When invoked, this skill should produce:
- Contract impact summary
- Change classification and version recommendation
- Required compatibility actions
- Test plan for producer/consumer/regression coverage
- Migration notes if any breaking behavior exists

## Skill Resources
- Versioning and compatibility policy: [contract-versioning-policy.md](references/contract-versioning-policy.md)
- Pull request quality gate checklist: [pr-checklist.md](assets/pr-checklist.md)
- Standardized contract change proposal form: [contract-change-template.md](assets/contract-change-template.md)

## Recommended Usage Pattern
1. Start from [contract-change-template.md](assets/contract-change-template.md) to frame the change.
2. Validate version bump and compatibility against [contract-versioning-policy.md](references/contract-versioning-policy.md).
3. Enforce delivery quality with [pr-checklist.md](assets/pr-checklist.md) before merge.
