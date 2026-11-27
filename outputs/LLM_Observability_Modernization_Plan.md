# LLM Observability Modernization Plan

This is a substantial modernization of the current Flask/SQLite prototype into a secure, testable internal observability service.

## Delivery phases

1. **Baseline:** reproducible Python tooling, pinned dependencies, characterization tests, and documented current behavior.
2. **Runtime foundation:** validated configuration, timeouts, bounded retries, structured failures, correlation IDs, migrations, UTC timestamps, and safer SQLite concurrency.
3. **Trustworthy metrics:** versioned model pricing, explicit unknown-cost states, validated pluggable evaluations, separate evaluation records, and safe judge execution.
4. **Dashboard product slice:** stable JSON contracts, pagination/filtering, authentication, production hardening, safe detail views, and browser tests.
5. **Operations:** retention, redaction, deletion, health/readiness, structured logs, deployment packaging, backup, migration, and rollback documentation.

## Recommended implementation order

1. Tooling and characterization tests
2. Configuration and provider-call policy
3. Failure-aware tracing and schema migrations
4. Cost and evaluation redesign
5. Dashboard/API contract and access control
6. Retention, redaction, operational metrics, and deployment

## Definition of done

- Clean install is reproducible.
- Tests, lint, type checks, and dependency checks pass offline/CI.
- Existing databases migrate without data loss.
- Every attempted provider call has a terminal status and correlation ID.
- Costs and evaluations identify estimates, versions, and failures.
- Dashboard/API access is protected and does not expose sensitive payloads by default.
- Retention/redaction/deletion behavior is tested.
- Production startup does not use Flask debug mode.

The detailed task breakdown with acceptance criteria, dependencies, verification steps, risks, and open questions is maintained in `tasks/plan.md`; the executable checklist is in `tasks/todo.md`.
