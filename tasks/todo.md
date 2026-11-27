# LLM Observability Modernization Tasks

## Phase 0: Baseline and contracts

- [ ] Task 1: Establish reproducible project tooling
- [ ] Task 2: Capture the current behavior with characterization tests

## Checkpoint: Baseline

- [ ] Clean install succeeds
- [ ] Baseline tests pass offline
- [ ] Public behavior and intentional breaking changes are documented

## Phase 1: Reliable runtime foundation

- [ ] Task 3: Introduce validated configuration and provider client policy
- [ ] Task 4: Harden provider calls and failure recording
- [ ] Task 5: Add schema migrations and trace-oriented persistence

## Checkpoint: Runtime foundation

- [ ] Mocked provider calls produce complete success/failure traces
- [ ] Existing database data survives migration
- [ ] Timeout, retry, persistence, and empty-state tests pass

## Phase 2: Trustworthy cost and evaluation

- [ ] Task 6: Implement explicit, versioned cost calculation
- [ ] Task 7: Redesign evaluation as validated, pluggable records
- [ ] Task 8: Add safe LLM-as-judge execution policy

## Phase 3: Secure and useful dashboard

- [ ] Task 9: Define and test the dashboard/API contract
- [ ] Task 10: Add dashboard access control and production hardening
- [ ] Task 11: Improve dashboard UX and data safety

## Checkpoint: Product slice

- [ ] Authenticated user can inspect filtered traces, failures, costs, and evaluations
- [ ] Sensitive payloads are protected in list views
- [ ] Browser tests pass for empty and populated databases

## Phase 4: Operations and release readiness

- [ ] Task 12: Add retention, redaction, and data lifecycle controls
- [ ] Task 13: Add observability for the observability service
- [ ] Task 14: Package and document deployment

## Final checkpoint: Release candidate

- [ ] Full verification suite passes
- [ ] Current-schema migration is tested
- [ ] Auth, retention, redaction, and error handling are verified
- [ ] Production startup, backup, and rollback are documented
- [ ] No secrets or sensitive fixtures are committed
