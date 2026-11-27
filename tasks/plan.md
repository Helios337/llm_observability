# Implementation Plan: LLM Observability Modernization

## Overview

Modernize the current single-user Flask/SQLite demo into a dependable LLM tracing and evaluation service. The first release will remain easy to run locally, but will have explicit configuration, reproducible dependencies, durable request/error records, trustworthy evaluation semantics, protected dashboard access, retention controls, and automated verification. The implementation should preserve the existing wrapper-oriented usage where practical while introducing stable boundaries for future Postgres, background jobs, and multi-user support.

## Assumptions and scope

- The current `main` branch is the baseline.
- The first target is a small internal deployment, not a hosted SaaS platform.
- SQLite remains supported for local/single-process use; Postgres support is designed for later, not forced into the first slice.
- Existing prompt/response history is valuable, so schema changes must be additive and migration-based.
- No provider credentials, prompts, responses, or user data should be added to tests, fixtures, or logs.

## Architecture decisions

- Add a typed configuration layer with environment-backed settings and explicit development/production modes.
- Split persistence into migrations, repositories, and domain records rather than keeping SQL and application behavior intertwined.
- Represent every request as a trace with status (`success`, `error`, `timeout`, `rate_limited`), timing, token usage, estimated/provider cost, and error metadata.
- Treat evaluations as separate records linked to a trace, allowing multiple evaluators and re-evaluation without overwriting the original call.
- Keep the synchronous wrapper API first; add an optional background evaluation path only after the synchronous correctness path is tested.
- Use server-rendered Flask endpoints initially, with JSON API contracts documented and tested before substantial dashboard changes.
- Default to safe local development settings; production startup must require an explicit production configuration and must never enable Flask debug mode.

## Task List

### Phase 0: Baseline and contracts

#### Task 1: Establish reproducible project tooling

**Description:** Add a modern Python project definition, supported Python version, pinned/locked dependency workflow, formatter, linter, type checker, and test runner. Keep `requirements.txt` only if needed for compatibility with the existing quick start.

**Acceptance criteria:**
- [ ] A fresh environment can install the project from the documented command.
- [ ] Dependency versions are reproducible through a committed lock or constraints file.
- [ ] Formatting, linting, type checking, and tests have documented commands.

**Verification:** Run the full tooling command in a clean virtual environment.

**Dependencies:** None

**Files likely touched:** `pyproject.toml`, lock/constraints file, `README.md`, `setup.sh`

**Estimated scope:** Medium

#### Task 2: Capture the current behavior with characterization tests

**Description:** Add tests for the existing wrapper, database, evaluator, and dashboard JSON contracts before changing behavior. Use mocked provider responses and temporary databases.

**Acceptance criteria:**
- [ ] Tests cover successful calls, failed calls, empty database metrics, recent-call serialization, and call/evaluation association.
- [ ] No test requires a real OpenRouter key or network access.
- [ ] The baseline test suite passes before modernization changes begin.

**Verification:** Run the test suite offline.

**Dependencies:** Task 1

**Files likely touched:** `tests/`, `llm_wrapper.py`, `database.py`, `dashboard.py`

**Estimated scope:** Medium

### Checkpoint: Baseline

- [ ] Clean install succeeds.
- [ ] Baseline tests pass offline.
- [ ] Public behavior and intentional breaking changes are documented.

### Phase 1: Reliable runtime foundation

#### Task 3: Introduce validated configuration and provider client policy

**Description:** Replace scattered environment reads and hard-coded model choices with a configuration object. Validate required credentials, model IDs, ports, database paths, request timeouts, retry limits, and development/production mode at startup.

**Acceptance criteria:**
- [ ] Missing API credentials produce a clear startup error when provider calls are enabled.
- [ ] Request timeout, retry, model, and database settings are configurable.
- [ ] Production mode cannot start with debug enabled or an unsafe default secret.

**Verification:** Unit-test valid, missing, malformed, and production configurations.

**Dependencies:** Tasks 1-2

**Files likely touched:** `config.py`, `llm_wrapper.py`, `dashboard.py`, `.env.example`, `README.md`

**Estimated scope:** Medium

#### Task 4: Harden provider calls and failure recording

**Description:** Add explicit timeouts, bounded retries with backoff for retryable failures, request correlation IDs, structured error categories, and consistent result types. Persist failed attempts without leaking secrets into logs.

**Acceptance criteria:**
- [ ] Timeout, authentication, rate-limit, provider, and malformed-response cases are distinguishable.
- [ ] Retries are bounded and only applied to retryable failures.
- [ ] Every attempted call has a correlation ID and terminal status.
- [ ] API keys and authorization headers never appear in logs or persisted records.

**Verification:** Mock each failure class and assert retry count, status, latency, and stored error metadata.

**Dependencies:** Task 3

**Files likely touched:** `llm_wrapper.py`, `models.py`, `logging_config.py`, `tests/`

**Estimated scope:** Large; split implementation into client policy and persistence if needed

#### Task 5: Add schema migrations and trace-oriented persistence

**Description:** Replace implicit table creation with versioned migrations. Add trace status, provider/model metadata, input/output token counts, provider cost when available, estimated cost, error fields, and UTC timestamps while retaining compatibility with existing `llm_calls` data.

**Acceptance criteria:**
- [ ] Existing databases migrate without losing calls or evaluations.
- [ ] New installs create the same schema through migrations.
- [ ] Queries use UTC timestamps and indexed fields for time, model, and status.
- [ ] Concurrent access has an explicit SQLite policy (WAL/busy timeout or documented single-writer constraint).

**Verification:** Test fresh migration, upgrade migration, rollback-safe failure behavior, and concurrent read/write smoke tests.

**Dependencies:** Tasks 2-4

**Files likely touched:** `database.py`, `migrations/`, `repositories/`, `tests/`

**Estimated scope:** Large

### Checkpoint: Runtime foundation

- [ ] A mocked provider call produces a complete success or failure trace.
- [ ] Existing database data survives migration.
- [ ] Tests cover timeout, retry, persistence, and empty-state behavior.

### Phase 2: Trustworthy cost and evaluation

#### Task 6: Implement explicit, versioned cost calculation

**Description:** Replace the substring-based free-model heuristic and universal token price with a pricing registry. Store input/output prices, pricing version, currency, and whether a value is provider-reported or estimated.

**Acceptance criteria:**
- [ ] Pricing is selected by provider/model configuration, not string matching.
- [ ] Unknown pricing is represented as unknown instead of silently reported as zero.
- [ ] Free models and paid models have regression tests.
- [ ] Dashboard totals distinguish estimated from provider-reported cost.

**Verification:** Test representative model configurations, missing pricing, and token-count edge cases.

**Dependencies:** Tasks 3 and 5

**Files likely touched:** `pricing.py`, `config.py`, `database.py`, `dashboard.py`, `tests/`

**Estimated scope:** Medium

#### Task 7: Redesign evaluation as validated, pluggable records

**Description:** Make rubric evaluation configurable and meaningful, validate weights and scores, implement the configured relevance criterion, and store evaluator name/version, individual criteria, raw feedback, and final score separately from the trace.

**Acceptance criteria:**
- [ ] Rubric weights must sum to 1.0 and criteria are validated.
- [ ] Relevance is based on explicit configured behavior, not a constant placeholder.
- [ ] Scores are always clamped to `[0, 1]` and malformed judge output is recorded as an evaluation error.
- [ ] Multiple evaluations can exist for one trace without overwriting history.

**Verification:** Test boundary scores, malformed judge output, missing fields, custom rubrics, and re-evaluation.

**Dependencies:** Tasks 4-5

**Files likely touched:** `evaluator.py`, `evaluation_models.py`, `repositories/`, `tests/`

**Estimated scope:** Large

#### Task 8: Add safe LLM-as-judge execution policy

**Description:** Bound judge input size, separate the response data from evaluator instructions as far as the provider API allows, require structured output or robust parsing, and make judge failures non-fatal to the original trace.

**Acceptance criteria:**
- [ ] Oversized prompts/responses are truncated or rejected with an explicit reason.
- [ ] Judge score parsing rejects out-of-range and ambiguous output.
- [ ] A judge failure leaves the original trace successful and records evaluation failure separately.
- [ ] Judge calls do not inflate primary request metrics.

**Verification:** Test prompt injection-like content, oversized content, malformed structured output, and provider failure.

**Dependencies:** Task 7

**Files likely touched:** `evaluator.py`, `llm_wrapper.py`, `tests/`

**Estimated scope:** Medium

### Phase 3: Secure and useful dashboard

#### Task 9: Define and test the dashboard/API contract

**Description:** Formalize metrics, traces, evaluations, pagination, filters, and error responses. Add API tests and consistent JSON error handling before changing the UI.

**Acceptance criteria:**
- [ ] Metrics have explicit null/unknown semantics.
- [ ] Recent calls support bounded pagination and model/status/time filters.
- [ ] All API error responses have stable status codes and JSON shapes.
- [ ] Empty database and partially evaluated traces render successfully.

**Verification:** Flask test-client coverage for every endpoint and filter combination.

**Dependencies:** Tasks 5-8

**Files likely touched:** `dashboard.py`, `api/`, `tests/`, `README.md`

**Estimated scope:** Large

#### Task 10: Add dashboard access control and production hardening

**Description:** Protect dashboard/API routes with a simple configurable authentication mechanism appropriate for the internal deployment, add security headers, disable debug in production, and document deployment behind a reverse proxy.

**Acceptance criteria:**
- [ ] Unauthenticated requests cannot read traces or metrics.
- [ ] Credentials/secrets are hashed or delegated to the deployment environment and never stored in source.
- [ ] Debug mode is impossible in production configuration.
- [ ] Responses include appropriate security headers and errors do not expose stack traces.

**Verification:** Authenticated/unauthenticated endpoint tests plus a production startup smoke test.

**Dependencies:** Tasks 3 and 9

**Files likely touched:** `auth.py`, `dashboard.py`, `config.py`, `tests/`, deployment docs

**Estimated scope:** Large

#### Task 11: Improve dashboard UX and data safety

**Description:** Add loading/error states, filters, trace detail view, visible data-quality indicators, and safe rendering of prompt/response content. Avoid shipping sensitive full payloads in list responses.

**Acceptance criteria:**
- [ ] UI shows provider failures, missing cost, and missing evaluation distinctly.
- [ ] List endpoints return previews; full payloads require an authorized detail request.
- [ ] Charts handle empty, sparse, and mixed-status datasets.
- [ ] Browser rendering continues to use encoded/text-safe output.

**Verification:** Browser smoke tests for empty, success, error, and long-content datasets.

**Dependencies:** Task 9-10

**Files likely touched:** `templates/dashboard.html`, static assets, `dashboard.py`, browser tests

**Estimated scope:** Large

### Checkpoint: Product slice

- [ ] An authenticated user can inspect filtered traces, failures, costs, and evaluations.
- [ ] Sensitive payloads are not exposed in list views.
- [ ] Browser tests pass against a populated and empty database.

### Phase 4: Operations and release readiness

#### Task 12: Add retention, redaction, and data lifecycle controls

**Description:** Add configurable retention periods, deletion by trace/time range, optional prompt/response redaction or hashing, and documentation describing what data is stored and why.

**Acceptance criteria:**
- [ ] Retention can be run repeatedly without corrupting data.
- [ ] Deletion removes linked evaluations and payloads according to policy.
- [ ] Redaction is applied before persistence, not only in the UI.
- [ ] The README documents sensitive-data handling and backup implications.

**Verification:** End-to-end lifecycle tests with synthetic sensitive markers.

**Dependencies:** Tasks 5 and 10

**Files likely touched:** `retention.py`, `database.py`, migrations, `config.py`, `tests/`, `README.md`

**Estimated scope:** Medium

#### Task 13: Add observability for the observability service

**Description:** Add structured application logs, health/readiness endpoints, internal counters for provider success/failure/retry/evaluation failure, and a bounded export path for metrics.

**Acceptance criteria:**
- [ ] Health checks distinguish process health from database/provider readiness.
- [ ] Logs include correlation IDs without prompts, responses, or secrets.
- [ ] Internal failure and latency metrics are available without querying raw payloads.

**Verification:** Health endpoint tests and log assertions with sensitive-data checks.

**Dependencies:** Tasks 4, 5, and 10

**Files likely touched:** `health.py`, `logging_config.py`, `dashboard.py`, `tests/`

**Estimated scope:** Medium

#### Task 14: Package and document deployment

**Description:** Add a production WSGI entry point, container or process-manager example, database backup guidance, environment reference, upgrade procedure, and release checklist.

**Acceptance criteria:**
- [ ] Production startup does not use Flask’s development server.
- [ ] Deployment documentation covers secrets, database persistence, migrations, backups, and rollback.
- [ ] A clean-machine smoke test follows the README successfully.

**Verification:** Build/start/health-check smoke test in a clean environment.

**Dependencies:** Tasks 10-13

**Files likely touched:** `wsgi.py`, deployment files, `README.md`, `.env.example`, CI workflow

**Estimated scope:** Medium

### Final checkpoint: Release candidate

- [ ] Full test, lint, type-check, and security/dependency checks pass.
- [ ] Migration tested from the current schema.
- [ ] Auth, retention, redaction, and error handling verified.
- [ ] Production startup and rollback procedure documented.
- [ ] Review confirms no secrets or sensitive fixture data are committed.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Existing SQLite data is malformed or partially migrated | High | Back up first, use additive migrations, test upgrade from a copied real database |
| Evaluation scores change after rubric improvements | Medium | Version evaluators and preserve historical scores rather than rewriting them |
| Provider pricing changes | Medium | Version pricing data and mark estimates clearly |
| Prompt/response data contains secrets or personal data | High | Redact before persistence, restrict detail access, add retention/deletion |
| Authentication scope expands into a full identity system | Medium | Start with deployment-appropriate internal auth and keep auth behind an interface |
| SQLite becomes a bottleneck | Medium | Add indexes/WAL now, measure, then introduce a repository-compatible Postgres backend |

## Open questions

- Is the intended first deployment single-user/local, or will multiple users access it over a network?
- Should raw prompts and responses be retained at all, or should production default to redacted/hashed payloads?
- Which providers besides OpenRouter must be supported in the first modernization release?
- Is LLM-as-judge required synchronously, or can evaluation be asynchronous to reduce request latency and failure coupling?
- What authentication mechanism is available in the target deployment environment?
