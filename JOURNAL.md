# Unit 7 - Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/40

**Issue title:** Add a "Copy link" button to share a public review summary

**Tier:** [ ] Tier 1  [x] Tier 2  [ ] Tier 3

**Why this issue (tier fit and scope):**

I chose Tier 2 because it matches my experience. I have built and shipped multi-module projects, including a monorepo clinic management platform and an Electron, React and TypeScript desktop app, so I am comfortable working across a front end and the backend behind it. I read the tier definitions before choosing. Tier 1 covers fixes contained in one or two files, and this issue goes beyond that: it touches the review page UI (`frontend/src/pages/ReviewPage.tsx`), the frontend service layer (`frontend/src/services/shareService.ts`), and the API routes (`api/routes/reviews.py`), and the three must work together to create, store, and serve a share link. Tier 3 covers full-system, infrastructure, or AI pipeline changes, and this issue does not touch those. The estimated effort is 5 to 8 hours, which fits the time available to me. The main risks are enforcing the 30-day expiration correctly and serving a read-only view without login while still exposing only the intended review summary. I plan to handle them by validating the link token and its expiry on the server for every request and by testing both an active and an expired link locally.

**Problem summary:**

- **What the issue is:** Users can view their review summary, but they cannot share it with someone else. The issue asks for a way to generate a shareable link that opens a read-only view of the summary, so a person can send their results to others without giving them access to the account.
- **What is currently missing:** There is no share feature. The app has no control for generating a link, no service call to request one, and no API route that serves a review summary to someone who is not logged in. The only way to show a summary to another person today is to give them access to the account.
- **What a successful fix accomplishes:** A user can generate a share link from the review page and copy it. Anyone with the link can open a read-only view of that review summary without logging in. The link stops working after 30 days, and the person opening it sees that it has expired.

**Branch name:** feat/40-share-review-link

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Unit 8 - Reproduction & solution planning

**Reproduction commit link:** https://github.com/shemarieirons/pathreview-ai201-fa26-howard/commit/e339f70

**Reproduction summary:**
I checked out main, ran the app locally, and confirmed the review page has no share control and the API has no share route. Without a share feature, a summary can only be viewed by someone with account access.

**PLAN.md link:** https://github.com/shemarieirons/pathreview-ai201-fa26-howard/blob/feat/40-share-review-link/PLAN.md

**Walkthrough video (recommended):** "not recorded"

**Blockers or open questions:**
None.

## Unit 9 - Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
All five sub-tasks from PLAN.md are implemented and committed: the review_share model and migration 003, the share service with token creation and a 30-day expiry check, the authenticated create route in reviews.py and the public read-only route in share.py, the frontend shareService.ts and ReviewPage share button with the new SharedReviewPage, and tests. On the backend, make check passes and make test-unit shows 394 passed and 53 xfailed, including 19 new tests in test_share_service.py and test_share_routes.py covering the 30-day expiry, expired and invalid tokens, and unauthenticated read-only access. No xfail marker is tied to this issue, so none needed removal. On the frontend, npm test -- --run passes with 29 tests across 5 files, including new tests for shareService, ReviewPage (copy link button), and SharedReviewPage.
**Next steps:**
Run the integration checks, fix the unawaited-coroutine warning in test_share_routes.py, check Google-style docstrings on the new public functions, open a draft PR and request peer feedback in Slack, then complete the PR template and mark the PR ready for review.

**Blockers:**
None. My first fork PR may need a maintainer to approve CI runs, so I am opening the draft PR today.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/100

**Branch:** feat/40-share-review-link

**What you built:**
I added expiring, read-only share links for review summaries. A logged-in user clicks Copy link on a completed review to generate a link, and anyone with that link can open a public read-only summary without logging in until the link expires 30 days after creation. Expiry and token validation are enforced on the server, and the public view returns only status, overall score, sections, and expiry date.

**Tests added or updated:**
- tests/unit/test_share_service.py: covers link creation for a completed review, reuse of an existing valid link, a new link when the old one has expired, unique tokens, expiry of exactly 30 days, a missing review returning 404, an incomplete review being rejected, an expired token returning 410, invalid and empty tokens returning 404, and the public schema omitting private fields such as owner and profile identifiers.
- tests/unit/test_share_routes.py: covers an authenticated user creating a link, authentication being required to create one, the public endpoint returning a summary without auth, expired and invalid tokens, and the public endpoint being read-only.
- frontend/src/pages/__tests__/ReviewPage.test.tsx: covers the Copy link button on a completed review summary.
- frontend/src/pages/__tests__/SharedReviewPage.test.tsx: covers displaying a valid shared summary and the expired and invalid link states.
- frontend/src/services/__tests__/shareService.test.ts: covers the share link API calls.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none