---
name: orchestrator-lifecycle-reliability
description: "Define deterministic orchestration lifecycle reliability for multi-agent CBAM workflows. Use when enforcing idempotent job execution, state-machine transitions, and error-code-driven retry/dead-letter behavior with exponential backoff."
argument-hint: "Provide workflow stages, job types, state transition rules, idempotency keys, and error-code handling policy"
user-invocable: true
disable-model-invocation: false
---

# Orchestrator Lifecycle Reliability

## Purpose
This skill standardizes reliability controls for multi-agent workflows (Data Miner, Auditor, Strategist) using deterministic state transitions, idempotent execution, and policy-driven failure handling.

Primary outcomes:
- Prevent race conditions and duplicate computation
- Enforce deterministic job lifecycle state machine behavior
- Route failures through explicit retry/dead-letter policies

## Scope
Applies to:
- End-to-end orchestrator job lifecycle management
- Async and background task execution
- Agent handoff boundaries and retries
- Failure recovery and dead-letter routing

## Mandatory Rules
1. Idempotent execution by design
- Every job operation must be idempotent.
- Repeated execution with same idempotency key must not create different side effects.
- Duplicate submit/process calls must resolve to same logical outcome.

2. Error-code-driven retry/dead-letter policy
- Handling must use domain error codes from agent-messaging-error-taxonomy.
- Transient errors must use exponential backoff with bounded retry budget.
- Permanent errors must be dead-lettered immediately or after policy-defined criteria.

3. Deterministic state machine lifecycle
- Job lifecycle must be modeled with explicit, validated state transitions.
- Silent failures and implicit state jumps are forbidden.
- Every transition must be observable and auditable.

## Canonical Job Envelope (Recommended)
Each orchestrated job should include:
- job_id
- correlation_id
- idempotency_key
- workflow_type
- current_state
- created_at
- updated_at
- retry_count
- max_retries
- last_error_code (optional)
- owner_agent (optional)
- trace_context

## State Machine Contract
Recommended states:
- PENDING
- VALIDATING
- PROCESSING
- RETRY_SCHEDULED
- COMPLETED
- FAILED
- DEAD_LETTERED
- CANCELLED (optional)

Required transition policy:
- PENDING -> VALIDATING
- VALIDATING -> PROCESSING
- PROCESSING -> COMPLETED
- PROCESSING -> RETRY_SCHEDULED (retryable error)
- RETRY_SCHEDULED -> PROCESSING (retry trigger)
- PROCESSING -> FAILED (non-retryable error)
- FAILED -> DEAD_LETTERED (if policy requires quarantine)

Forbidden transitions:
- COMPLETED -> PROCESSING
- DEAD_LETTERED -> PROCESSING (without explicit replay workflow)
- Any transition without transition_reason and timestamp

## Idempotency Rules
1. Key generation
- Idempotency key must be deterministic per business operation.
- Same operation request should map to same key.

2. Deduplication behavior
- If key already exists and terminal result available, return stored result.
- If key exists in active state, return current status instead of re-running.

3. Side-effect safety
- External writes must be protected by idempotency checks.
- Partial completion markers must support safe re-entry.

## Error Handling Integration
Use error categories from agent-messaging-error-taxonomy:
- Transient examples: EXT_*, ORCH_RETRYABLE_*
- Permanent examples: DQ_*, LEGAL_*, CONTRACT_* (unless policy says otherwise)

For each error code define:
- retryable: true/false
- max_attempts
- backoff_base_seconds
- backoff_multiplier
- max_backoff_seconds
- dead_letter_on_exhaustion: true/false

## Exponential Backoff Policy
Recommended formula:
- delay = min(max_backoff_seconds, backoff_base_seconds * (backoff_multiplier ^ attempt_index))

Required controls:
- Bounded retry budget
- Jitter strategy (optional but recommended for thundering herd reduction)
- Retry audit log with attempt number and next schedule time

## Dead-Letter Contract
A dead-letter record should include:
- dead_letter_id
- job_id
- correlation_id
- final_state
- failure_error_code
- failure_summary
- retry_history
- payload_snapshot_ref
- quarantined_at
- replay_eligible

Dead-letter is mandatory when:
- Retry budget exhausted for retryable errors
- Non-retryable critical errors occur
- State machine invariants are violated

## When To Use
Use this skill when:
- Designing new orchestrated job workflows
- Hardening retry and failure handling behavior
- Preventing duplicate calculations and race conditions
- Refactoring state transition logic into explicit machine rules
- Building replay/forensics pipeline for failed jobs

Trigger words:
- orchestrator lifecycle, state machine, idempotency, retry policy, exponential backoff, dead-letter, reliability

## Step-by-Step Procedure
1. Define workflow and state model
- Enumerate states, allowed transitions, and invariants.
- Define terminal and non-terminal states.

2. Implement idempotency boundaries
- Assign idempotency key strategy for submit/process operations.
- Add dedup checks at all side-effect boundaries.

3. Bind error code policies
- Import taxonomy mapping from agent-messaging-error-taxonomy.
- Configure retryability and dead-letter behavior per code.

4. Configure retry scheduler
- Apply exponential backoff formula and retry limits.
- Persist retry metadata for audit and observability.

5. Enforce transition guards
- Validate every transition against allowed-state matrix.
- Reject illegal transitions with explicit orchestration error code.

6. Implement dead-letter workflow
- Persist failed job context and diagnostics.
- Expose replay eligibility and manual intervention path.

7. Validate determinism
- Re-run same job inputs and verify identical final state/result behavior.
- Ensure no hidden side effects in retry/replay paths.

## Required Decision Points
1. Retry vs fail-fast
- Retry only error codes explicitly marked retryable.
- Fail-fast for deterministic business/legal/contract violations.

2. Dead-letter vs cancel
- Dead-letter for diagnosable recoverable pipeline failures.
- Cancel only for user/system-initiated interruption scenarios.

3. Replay policy
- Replay allowed only with preserved original envelope and trace context.
- Replayed jobs must create linked audit trail, not overwrite history.

## Standard Lifecycle Event Contract
Each lifecycle event should include:
- event_id
- job_id
- correlation_id
- from_state
- to_state
- transition_reason
- error_code (optional)
- actor
- occurred_at

## Recommended Error Codes (Orchestrator)
- ORCH_DUPLICATE_IDEMPOTENCY_KEY
- ORCH_INVALID_STATE_TRANSITION
- ORCH_RETRY_BUDGET_EXHAUSTED
- ORCH_DEAD_LETTER_REQUIRED
- ORCH_STATE_MACHINE_INVARIANT_BROKEN
- ORCH_REPLAY_CONTEXT_MISSING

## Quality Gates
A lifecycle reliability change is complete only if all pass:
- State machine transition matrix tests pass
- Idempotency dedup tests pass for duplicate submits/process calls
- Retry policy tests pass with exponential backoff expectations
- Dead-letter routing tests pass on permanent/exhausted failures
- Silent-failure detection and observability checks pass

## Anti-Patterns
- Using status strings without transition validation
- Retrying non-retryable deterministic errors
- Reprocessing completed jobs without idempotency guard
- Hiding failure by leaving jobs in perpetual PROCESSING state
- Dead-letter records without payload/context for forensic replay

## Example Prompt Starters
- "Use orchestrator-lifecycle-reliability to define an idempotent state machine for Data Miner -> Auditor -> Strategist workflow."
- "Apply orchestrator-lifecycle-reliability to map taxonomy error codes to retry/backoff/dead-letter policies."
- "Use orchestrator-lifecycle-reliability to audit current job lifecycle for race conditions and duplicate processing risks."

## Output Contract For This Skill
When invoked, this skill should produce:
- Deterministic state machine specification
- Idempotency and deduplication strategy
- Error-code-to-reaction policy matrix
- Exponential backoff configuration plan
- Dead-letter and replay governance checklist
