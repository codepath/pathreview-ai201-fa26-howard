## Unit 7 — Issue selection

**Issue link:** [Issue #65](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/65)

**Issue title:** review_service unit tests misconfigure async mocks

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**

The tests mix asynchronous and synchronous behavior, but the final assertions do not correctly account for that distinction. As a result, some tests fail because their mocks and assertions do not match how the service actually calls the database. The fix should make each test reflect the correct async boundaries and expected number of database calls.

**Branch name:** `fix/65-review-service-async-mocks`

## Is This Issue Right for Me?

**Understanding the issue:** I can explain the issue in my own words: the review-service tests use asynchronous mocks for both database operations and result-processing methods, even though only the database operations are awaited. The tests should use `AsyncMock` for awaited calls and regular `Mock` objects for synchronous result methods.

**Affected code:** I located and read `core/services/review_service.py` and `tests/unit/test_review_service.py`, including `create_review`, `get_review`, and `list_reviews`.

**Definition of done:** The tests should match the service's actual async boundaries, avoid un-awaited coroutine warnings, and assert the correct number of database calls. `list_reviews` should account for its two database queries.

**Tier fit:** This is a Tier 1 issue because it is a localized unit-test fix in one area of the codebase and does not require changing application behavior.

**Codebase readiness:** I read the relevant service functions and the existing test fixtures and mock patterns, so I can identify which calls are asynchronous and which are synchronous.

**Scope and time:** The work is limited to correcting test mocks, removing obsolete expected-failure markers, updating assertions, and rerunning the focused tests. This is realistic for Units 8–9.

**Claims and dependencies:** The issue was added to the cohort ledger, and I found no unresolved code dependency that blocks this fix.

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger



## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
- Completed PLAN.md sub-task 1: replaced the `AsyncMock` result objects with regular `Mock` result objects (via a `make_result()` helper), while keeping `AsyncMock` for the awaited `db.execute()`, `db.commit()`, and `db.refresh()` calls.
- Completed PLAN.md sub-task 2: updated the `get_review()` tests so `scalars().first()` synchronously returns the expected review or `None`, and they assert `execute` was awaited exactly once.

**Next steps:**
- PLAN.md sub-task 3: update the `list_reviews()` tests so `scalars().all()` returns plain lists and assertions account for its two queries (count + page).
- PLAN.md sub-task 4: remove the issue #65 `xfail` markers and replace weak assertions (e.g. `len(reviews) > 0 or len(reviews) == 0`) with exact ones.
- PLAN.md sub-task 5: run the focused review-service tests, then `make test-unit` and `make check`.

**Blockers:** None.

---

### Check-in 2 (end of week)

**PR link:** [PR #95](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/95)

**Branch:** `fix/65-review-service-async-mocks`

**What you built:**
I fixed the review_service unit tests so their mocks match the service's real async boundaries: awaited database calls (`execute`, `commit`, `refresh`) use `AsyncMock`, while SQLAlchemy result methods (`scalars().first()` / `scalars().all()`) use synchronous `Mock`s. I removed the six issue #65 `xfail` markers and tightened the assertions so they check exact return values and the correct number of awaited database queries.

**Tests added or updated:**
Modified `tests/unit/test_review_service.py` (no production code changed). The tests now cover: `get_review()` returning the owned review, or `None` when no owned review is found, with exactly one awaited query; `list_reviews()` returning the exact reviews list and total count as a `(reviews, total)` tuple with exactly two awaited queries (count + page); page 2 with `page_size=20` producing a query offset of 20; and `create_review()` creating a review with `pending` status and calling `add`, `commit`, and `refresh`. All 19 tests pass with no un-awaited coroutine warnings.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none
