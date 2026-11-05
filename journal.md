## Unit 7 — Issue selection

**Issue link:** [https://github.com/codepath/pathreview-ai201-fa26-howard/issues/65]

**Issue title:** [review_service unit tests misconfigure async mocks]

**Tier:** [ x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
[In 3–5 sentences, in your own words: what the issue is (not a copy-paste of
the title), what is currently broken or missing, and what a successful fix
would accomplish. Naming the part of the codebase it affects is helpful context.]

The tests mix asynchronous and synchronous behavior, but the final assertions do not correctly account for that distinction. As a result, some tests fail because their mocks and assertions do not match how the service actually calls the database. The fix should make each test reflect the correct async boundaries and expected number of database calls.

**Branch name:** [fix/65-review-service-async-mocks]

Is this issue right for me

Understanding the issue: I can explain the issue in my own words: the review-service tests use asynchronous mocks for both database operations and result-processing methods, even though only the database operations are awaited. The tests should use AsyncMock for awaited calls and regular Mock objects for synchronous result methods.

Affected code: I located and read core/services/review_service.py and tests/unit/test_review_service.py, including create_review, get_review, and list_reviews.

Definition of done: The tests should match the service's actual async boundaries, avoid un-awaited coroutine warnings, and assert the correct number of database calls. list_reviews should account for its two database queries.

Tier fit: This is a Tier 1 issue because it is a localized unit-test fix in one area of the codebase and does not require changing application behavior.

Codebase readiness: I read the relevant service functions and the existing test fixtures and mock patterns, so I can identify which calls are asynchronous and which are synchronous.

Scope and time: The work is limited to correcting test mocks, removing obsolete expected-failure markers, updating assertions, and rerunning the focused tests. This is realistic for Units 8–9.

Claims and dependencies: The issue was added to the cohort ledger, and I found no unresolved code dependency that blocks this fix.

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x ] Issue added to cohort ledger