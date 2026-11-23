## Solution plan

**Issue link:** [Issue #65](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/65)

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

The review service awaits database operations such as `execute()`, `commit()`, and
`refresh()`, but it reads the returned SQLAlchemy results synchronously through
`scalars().first()` and `scalars().all()`. The tests currently use `AsyncMock`
for the entire result object, which does not match the service's actual call
pattern and can create coroutine errors or un-awaited coroutine warnings.

Expected behavior: awaited database methods use `AsyncMock`, synchronous result
methods use regular `Mock`, and assertions match the service's real database
call count. `get_review()` should execute one query; `list_reviews()` should
execute two queries, one for the total and one for the requested page.

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

- `tests/unit/test_review_service.py`
	- Fix result-chain mocks for `get_review()` and `list_reviews()`.
	- Update database call-count assertions.
	- Remove obsolete `xfail` markers after the tests pass.
- `core/services/review_service.py`
	- Read-only reference for the async boundaries and query behavior; no
		application change is expected.
- `PLAN.md`
	- Document the implementation and validation plan.

### Plan
What are the steps to fix this issue?
Break it into 3–5 concrete sub-tasks.

1. Replace `AsyncMock` result objects with `Mock` result objects, while keeping
	 `AsyncMock` for `db.execute()`, `db.commit()`, and `db.refresh()`.
2. Update `get_review()` tests so `scalars().first()` returns the expected
	 review or `None` synchronously.
3. Update `list_reviews()` tests so `scalars().all()` returns normal lists and
	 assertions account for its two database queries.
4. Remove the issue-specific `xfail` markers and strengthen assertions where
	 they currently accept any result.
5. Run the focused review-service tests, then run the unit-test suite if the
	 focused tests pass.

### Inputs & outputs
What does your fix take as input? What should it produce or change?

Inputs are mocked async database sessions, mocked SQLAlchemy result objects,
UUIDs, and the existing review-service functions. The fix should change only
the unit-test setup and assertions. It should produce passing tests without
un-awaited coroutine warnings and without changing production behavior.

### Risks & unknowns
What could go wrong? What are you still unsure about?

- A result chain may still be configured as asynchronous if a test does not
	match the service's actual `await` usage.
- `list_reviews()` intentionally executes two queries, so an assertion expecting
	one call would be incorrect.
- Removing `xfail` markers before correcting every affected mock could turn
	known expected failures into unexplained failures.
- The broader unit suite may contain unrelated pre-existing failures; those
	should be reported separately from this focused fix.

### Edge cases
What inputs or states should your fix handle gracefully?

- `get_review()` returns a review when the query result contains one.
- `get_review()` returns `None` when no owned review is found.
- `list_reviews()` handles an empty result list and still returns an integer
	total.
- `list_reviews()` handles page 1 and later pages while issuing both expected
	queries.
- Tests must preserve the asynchronous test boundary by using
	`@pytest.mark.asyncio`, `async def`, and `await` for service calls.