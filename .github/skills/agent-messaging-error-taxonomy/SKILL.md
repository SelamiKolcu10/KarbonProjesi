---
name: agent-messaging-error-taxonomy
description: "Standardize multi-agent message envelopes and define a domain-specific error taxonomy with deterministic handling contracts for Data Miner, Auditor, Strategist, and orchestration flows. Use when implementing inter-agent messaging, traceability, and response policies for categorized failures."
argument-hint: "Provide producer/consumer agents, message types, required trace fields, error categories, and desired handling policy"
user-invocable: true
disable-model-invocation: false
---

# Agent Messaging and Error Taxonomy

## Purpose
This skill defines a strict inter-agent communication protocol and a domain-specific error taxonomy for multi-agent CBAM workflows.

Primary outcomes:
- Standard message envelope across Data Miner, Auditor, Strategist, and Orchestrator
- End-to-end traceability with correlation metadata
- Deterministic error classes and handling behavior contracts

## Scope
Applies to:
- Agent-to-agent request/response messages
- Event-style notifications and async job status updates
- Validation, calculation, compliance, and reporting failures
- API boundary mappings for internal agent errors

## Mandatory Rules
1. Standard message envelope for every inter-agent message
- Every message MUST include Correlation ID, timestamp, sender, and receiver.
- Envelope metadata is mandatory regardless of payload type.
- Messages without required envelope fields are invalid and rejected.

2. Domain-specific error taxonomy with stable error codes
- Generic runtime exceptions are not valid integration contracts.
- Errors must be emitted as categorized project-level error codes.
- Error code namespace must be versioned and backward-compatible.

3. Explicit handling contract per error class
- Each error class must define exactly how the system reacts:
  - retry
  - fallback
  - dead-letter/stop
- Handling behavior must be deterministic and documented.

## Canonical Message Envelope Contract
Each message should include:
- message_id
- correlation_id
- causation_id (optional but recommended)
- sent_at (UTC ISO-8601)
- producer_agent
- consumer_agent
- message_type
- schema_version
- payload
- trace_context
- priority (optional)
- idempotency_key (optional for commands)

## Envelope Validation Rules
1. Required metadata
- correlation_id is mandatory and immutable through the workflow chain.
- sent_at must be present and parseable as UTC timestamp.
- producer_agent and consumer_agent must be explicit identifiers.

2. Schema controls
- schema_version must be provided for envelope and payload contracts.
- payload validation must run after envelope validation.

3. Trace controls
- trace_context must carry run/job identifiers where available.
- nested calls should preserve correlation_id and set causation_id correctly.

## Error Taxonomy Model
Each error class definition should include:
- error_code
- error_category
- severity
- retry_policy
- fallback_policy
- dead_letter_policy
- http_mapping (if surfaced via API)
- description
- version

Recommended top-level categories:
- DQ: Data quality errors
- MATH: Mathematical tolerance/precision errors
- LEGAL: Regulatory compliance and legal-reference errors
- CONTRACT: Schema/envelope/compatibility errors
- ORCH: Orchestration lifecycle and state errors
- EXT: External dependency/provider errors

## Recommended Error Code Examples
Data Quality:
- DQ_REQUIRED_FIELD_MISSING
- DQ_PHYSICS_IMPOSSIBLE_VALUE
- DQ_CAPACITY_LIMIT_EXCEEDED

Math/Tolerance:
- MATH_TOLERANCE_EXCEEDED
- MATH_DECIMAL_POLICY_VIOLATION
- MATH_NONDETERMINISTIC_RESULT

Legal:
- LEGAL_REFERENCE_MISSING
- LEGAL_TEMPORAL_VERSION_MISMATCH
- LEGAL_CLAUSE_NOT_APPLICABLE

Contract/Messaging:
- CONTRACT_ENVELOPE_INVALID
- CONTRACT_SCHEMA_VERSION_UNSUPPORTED
- CONTRACT_PAYLOAD_TYPE_MISMATCH

Orchestration:
- ORCH_JOB_NOT_FOUND
- ORCH_INVALID_STATE_TRANSITION
- ORCH_RETRY_BUDGET_EXHAUSTED

## Handling Policy Contract
For each error code, define these policies explicitly:
1. Retry policy
- retryable: true/false
- max_attempts
- backoff_strategy
- retry_window

2. Fallback policy
- fallback_enabled: true/false
- fallback_action
- fallback_constraints

3. Dead-letter policy
- dead_letter_on_exhaustion: true/false
- dead_letter_topic_or_store
- required_diagnostics

## Standard Reaction Matrix
Baseline reaction strategy:
- CRITICAL + non-retryable -> dead-letter and stop downstream progression
- ERROR + retryable -> bounded retry then dead-letter
- WARNING -> continue with tagged warning context
- INFO -> log only

Do not allow implicit behavior. Reaction must be defined by code-level policy.

## When To Use
Use this skill when:
- Defining or refactoring inter-agent message contracts
- Implementing error propagation between agents
- Standardizing retry/fallback/dead-letter behavior
- Creating incident triage and observability mappings
- Aligning API responses with internal domain error model

Trigger words:
- message envelope, correlation id, error taxonomy, retry policy, dead-letter, fallback, agent communication

## Step-by-Step Procedure
1. Define message boundaries
- Identify producer/consumer pairs and message types.
- Define command, event, and response envelope requirements.

2. Enforce canonical envelope
- Add required metadata fields and validation.
- Ensure correlation_id propagation and causation chaining.

3. Define taxonomy and codes
- Classify domain failures into stable categories.
- Assign deterministic error codes and severity.

4. Attach handling contracts
- Configure retry/fallback/dead-letter per code.
- Set bounded retry and non-ambiguous stop conditions.

5. Implement error transport mapping
- Map internal error code to standardized agent response shape.
- Add API/http mapping only at boundary adapters.

6. Validate traceability and behavior
- Run tests for envelope propagation across multi-agent path.
- Run tests for each error class reaction branch.

7. Publish governance artifacts
- Version error catalog.
- Document policy changes and migration notes.

## Required Decision Points
1. Retry eligibility
- Retry only transient errors with explicit retryable=true.
- Never retry deterministic data or legal validity failures.

2. Fallback eligibility
- Fallback allowed only when business-safe and auditable.
- Fallback must be tagged in result metadata.

3. Dead-letter routing
- Dead-letter required for exhausted retries and non-recoverable failures.
- Include envelope + error diagnostics for replay/forensics.

## Standard Error Event Contract
Each emitted error event should include:
- event_id
- correlation_id
- causation_id
- error_code
- error_category
- severity
- producer_agent
- failed_component
- message
- diagnostics
- handling_decision (retry, fallback, dead_letter, stop)
- occurred_at

## Quality Gates
A messaging/taxonomy change is complete only if all pass:
- Envelope schema validation enforced on all agent boundaries
- Correlation id propagation tests pass
- Error code catalog version updated
- Retry/fallback/dead-letter policy defined for all new codes
- Deterministic reaction tests pass per error category
- Observability logs include envelope and decision metadata

## Anti-Patterns
- Using bare ValueError/Exception as cross-agent contract
- Missing correlation_id in async flows
- Retrying non-retryable business/legal errors
- Silent fallback without tagged diagnostics
- Dead-letter without enough context for replay

## Example Prompt Starters
- "Use agent-messaging-error-taxonomy to define a canonical envelope for Data Miner -> Auditor messages with correlation and causation tracing."
- "Apply agent-messaging-error-taxonomy to classify current errors and attach retry/fallback/dead-letter policies."
- "Use agent-messaging-error-taxonomy to design a versioned error code catalog for API and orchestrator integration."

## Output Contract For This Skill
When invoked, this skill should produce:
- Canonical message envelope schema
- Versioned error taxonomy and code catalog
- Reaction policy matrix (retry/fallback/dead-letter)
- Traceability validation checklist
- Migration notes for backward-compatible adoption
