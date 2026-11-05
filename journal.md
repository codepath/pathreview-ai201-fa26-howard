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

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x ] Issue added to cohort ledger