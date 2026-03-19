---
name: architecture-guardian-scaffolding
description: "Act as a meta-architecture guardian that enforces long-term compliance with core CBAM skills and auto-scaffolds new agents/modules against mandatory standards (contracts, deterministic math, taxonomy, orchestration lifecycle, and governance gates). Use when adding any new agent, feature, or module."
argument-hint: "Describe the new agent/module scope, data flow, dependencies, and intended behaviors to generate a fully compliant architecture scaffold"
user-invocable: true
disable-model-invocation: false
---

# Architecture Guardian Scaffolding

## Purpose
This meta-skill acts as the system-level Chief Architect guardrail. It ensures every new agent, feature, or module is scaffolded in full compliance with established CBAM architecture standards and does not erode core system integrity.

Primary outcomes:
- Persist architecture rules across long-term development
- Auto-scaffold new additions against the 15 core skill standards
- Detect and warn on requests that could break core math/rule governance

## Scope
Applies to:
- New agent/module/feature proposals
- Major refactors touching cross-agent contracts and orchestration
- Any change that could affect carbon-math, data quality governance, or lifecycle reliability
- Pre-implementation architecture review checkpoints

## Mandatory Rules
1. Always enforce baseline architecture standards during scaffolding
- Every new addition must be checked against core standards: contract governance, deterministic math, ingestion quality, error taxonomy, lifecycle reliability, explainability, and reporting stability.
- No module may be scaffolded outside these guardrails.
- Compliance must be explicit, not assumed.

2. Auto-checklist for new agent onboarding
- For every new agent/module, generate mandatory integration checklist covering:
  - data ingestion and mapping boundary
  - messaging envelope and error taxonomy alignment
  - orchestrator lifecycle and retry/dead-letter integration
- Checklist must be validated before implementation completion.

3. Protect core heart of system (carbon-math and rule-engine)
- If request can alter core math semantics or central rule-engine behavior, emit architecture risk warning.
- Require explicit developer confirmation/approval before proceeding.
- Record rationale and scope of approved exception.

## Core Skills Compliance Matrix
This skill must check alignment with these architecture pillars:
1. agent-contract-registry
2. payload-mapping-canonicalization
3. carbon-math-governance
4. golden-baseline-regression
5. explainability-evidence-composer
6. data-quality-rule-engine
7. data-provenance-confidence-calibration
8. multi-format-ingestion-assurance
9. agent-messaging-error-taxonomy
10. orchestrator-lifecycle-reliability
11. cbam-regulation-delta-tracker
12. financial-stress-sensitivity-analyzer
13. scenario-simulation-playbook
14. api-contract-consistency-guard
15. reporting-payload-design-system

Any non-applicable skill must be explicitly marked with justification.

## Scaffolding Contract
Each scaffolding result should include:
- module_blueprint_id
- target_component_name
- architecture_scope
- dependency_map
- compliance_matrix
- risk_flags
- approval_requirements
- generated_at
- guardian_version

## New Agent Onboarding Checklist (Mandatory)
1. Data Flow and Contracts
- Define inbound/outbound payload schemas.
- Validate against agent-contract-registry.
- Define mapping/canonicalization path where needed.

2. Error and Messaging
- Define message envelope fields (correlation_id, timestamp, producer/consumer).
- Assign domain error codes from taxonomy.
- Define retry/fallback/dead-letter behavior.

3. Lifecycle and Operations
- Integrate orchestrator state machine transitions.
- Ensure idempotency for job execution boundaries.
- Define observability events for lifecycle transitions.

4. Governance and Safety
- Check carbon-math-governance impact.
- Check data-quality-rule-engine impact.
- Check explainability and confidence metadata requirements.

5. Output and Integration
- Ensure reporting DTO compatibility.
- Verify API contract consistency impact.
- Define regression and compatibility tests.

## Core Protection Policy (High-Risk Guard)
High-risk request triggers include:
- Modifying central emission/tax formulas
- Changing governed coefficients or precision behavior
- Altering rule-engine semantics or threshold interpretation
- Bypassing lifecycle retry/dead-letter policy

Required response when triggered:
1. Emit ARCH_GUARD_HIGH_RISK_CHANGE warning.
2. Show impacted core components and expected risks.
3. Request explicit approval with rationale.
4. Require post-change regression + explainability validation.

## When To Use
Use this skill when:
- Adding a new agent to the multi-agent workflow
- Introducing new module with cross-cutting concerns
- Reviewing architecture compliance before merge
- Preparing a scalable blueprint for future expansion
- Evaluating risky changes touching core governance logic

Trigger words:
- architecture guard, scaffolding, new agent onboarding, compliance matrix, core protection, meta skill, chief architect

## Step-by-Step Procedure
1. Ingest change proposal
- Parse requested agent/module purpose, boundaries, and dependencies.

2. Build architecture profile
- Identify data, messaging, lifecycle, governance, and reporting touchpoints.

3. Generate compliance matrix
- Evaluate proposal against all 15 core skills.
- Mark each as compliant, non-compliant, or not-applicable with reason.

4. Generate onboarding checklist
- Produce mandatory integration tasks and validation items.
- Include acceptance criteria and blocking conditions.

5. Run core protection checks
- Detect potential impact on carbon-math and rule-engine heart.
- If high-risk, issue warning and request explicit approval.

6. Produce scaffold blueprint
- Output recommended module structure, contracts, and policy bindings.
- Include required tests and rollout gates.

7. Validate and sign off
- Confirm all blocking compliance gaps resolved.
- Mark proposal as READY or BLOCKED with reasons.

## Required Decision Points
1. Applicability decisions
- Determine which of 15 skills are mandatory vs context-optional for target module.

2. Blocking threshold
- Decide whether identified gaps are warning-level or block-level.

3. Approval requirement
- Decide if change requires explicit human approval (core risk triggered).

4. Rollout mode
- Choose safe rollout strategy: staged, feature-flagged, or direct (if low risk).

## Compliance Failure Codes
Recommended codes:
- ARCH_GUARD_COMPLIANCE_GAP
- ARCH_GUARD_MISSING_ONBOARDING_CHECKS
- ARCH_GUARD_CONTRACT_ALIGNMENT_FAILED
- ARCH_GUARD_LIFECYCLE_POLICY_MISSING
- ARCH_GUARD_HIGH_RISK_CHANGE
- ARCH_GUARD_APPROVAL_REQUIRED

Each failure should include:
- code
- target_component
- affected_skill
- gap_description
- severity
- required_action
- trace_id

## Quality Gates
A scaffolding decision is complete only if all pass:
- 15-skill compliance matrix generated
- New-agent onboarding checklist completed
- Messaging/taxonomy/lifecycle integration validated
- Core protection checks executed
- Required approvals captured for high-risk changes
- Regression and release gates defined

## Anti-Patterns
- Adding new agents without cross-skill compliance review
- Treating core math or rule-engine changes as low risk by default
- Skipping idempotency and state machine integration in orchestration
- Deferring error taxonomy decisions until runtime failures
- Coupling UI needs directly into backend contracts during scaffolding

## Example Prompt Starters
- "Use architecture-guardian-scaffolding to onboard a new Compliance Agent and generate a full 15-skill compliance matrix."
- "Apply architecture-guardian-scaffolding to scaffold a new module and validate messaging, lifecycle, and reporting integration checklists."
- "Use architecture-guardian-scaffolding to assess whether this requested math change is high risk and requires explicit approval."

## Output Contract For This Skill
When invoked, this skill should produce:
- Architecture compliance matrix across core skills
- New-agent/module integration checklist with pass/fail criteria
- Core-risk warning and approval requirements (if triggered)
- Recommended scaffold blueprint and dependency map
- Final readiness decision (READY/BLOCKED) with actionable next steps
