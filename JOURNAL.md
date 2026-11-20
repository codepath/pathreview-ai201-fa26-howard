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

# Unit 8 - Reproduction & solution planning

**Reproduction commit link:** https://github.com/shemarieirons/pathreview-ai201-fa26-howard/commit/e339f70

**Reproduction summary:**
I checked out main, ran the app locally, and confirmed the review page has no share control and the API has no share route. Without a share feature, a summary can only be viewed by someone with account access.

**PLAN.md link:** https://github.com/shemarieirons/pathreview-ai201-fa26-howard/blob/feat/40-share-review-link/PLAN.md

**Walkthrough video (recommended):** "not recorded"

**Blockers or open questions:**
None.

# Unit 9 - Solution building & PR submission

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

## PR Description
## Summary
Adds expiring, read-only share links for review summaries. An authenticated user can generate a share link for a completed review from the review page using the Copy link button. Anyone with the link can open a read-only public summary without logging in, until the link expires 30 days after creation. The public view exposes only the status, overall score, sections, and expiry date, and omits identifiers such as owner email, user ID, review ID, and profile ID. Expiry and token validation are enforced on the server for every request, not only in the UI.

## Issue
Closes https://github.com/codepath/pathreview-ai201-fa26-howard/issues/40

Note: the issue title mentions a "Copy link" button, but the issue body asks for a no-login, read-only share link that expires after 30 days. This PR implements the full behavior described in the body, including the Copy link button.

## Changes
- Added the `ReviewShareLink` model (`core/models/review_share.py`), a relationship on `Review`, and Alembic migration `003_add_review_share_links.py`
- Added `core/services/share_service.py`: creates a share link for a completed review, reuses an existing valid link, creates a new link when the old one has expired, sets expiry to exactly 30 days, and resolves tokens (expired returns 410, unknown or empty returns 404, incomplete review cannot be shared)
- Added an authenticated create route in `api/routes/reviews.py` and a public read-only route in `api/routes/share.py`, registered in `api/main.py`
- Added public and share response schemas in `api/schemas/review.py` that exclude private fields
- Frontend: `shareService.ts` API calls, a Copy link button with confirmation on `ReviewPage.tsx`, a new `SharedReviewPage.tsx` (read-only view with an expired-link state), a route in `App.tsx`, and shared types in `types/index.ts`
- Added tests: `tests/unit/test_share_service.py`, `tests/unit/test_share_routes.py`, `ReviewPage.test.tsx`, `SharedReviewPage.test.tsx`, and `shareService.test.ts`

## Testing
- [x] **CI is green on this PR (all five jobs)** - required for review
- [x] Unit tests pass (`make test-unit`)
- [x] Integration tests pass (`make test-integration`)
- [x] Linter passes (`make lint`)
- [x] Type checker passes (`make typecheck`)
- [x] New/updated tests cover the changes
- [ ] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any
      matching suppression in `pyproject.toml`)

Local results: `make check` is clean. `make test-unit` gives 394 passed and 53 xfailed, including 19 new tests for the share service and routes. Frontend tests (`npm test -- --run`) give 29 passed across 5 files.

This is a new feature, not a seeded bug, so no xfail marker is tied to it and none was removed.

**Manual verification steps:**
1. Apply the migration and start the app: `alembic upgrade head`, then start the API and frontend (frontend at http://localhost:5173).
2. Log in with the test credentials from the docs and open a completed review.
3. Click **Copy link**. A share URL is created and copied, and a confirmation message appears.
4. Open the copied URL in a private or incognito window without logging in. The read-only summary loads, with no edit controls and no private fields such as owner email, user ID, review `id`, or `profile_id`.
5. Change the last characters of the token in the URL and reload. A not-found message appears and the page does not crash.
6. To test expiry, set `expires_at` to a past date on that link's row in `review_share_links` and reload the shared URL. The expired-link message appears.
7. Try to share a review that is not completed. The request is rejected with 400 ("Only completed reviews can be shared") and no link is created.
8. Click **Copy link** again on a review that already has a valid link. The same link is returned.

## Screenshots / Demo
Not included

## Notes for Reviewers
- **Privacy:** please check the public schema in `api/schemas/review.py` and the public route in `api/routes/share.py`. They are meant to return only the summary fields and nothing identifying the owner. `test_share_service.py` has tests for this.
- **Expiry:** it is enforced server-side in `share_service.py` on every request, with the expiry set to exactly 30 days at creation.
- **Migration:** `003_add_review_share_links.py` adds one table. Please confirm it applies cleanly on top of the current head.
- **Link reuse:** creating a link for a review that already has a valid one returns the existing link instead of making a new one. An expired link is replaced with a new one.
- **First fork PR:** workflows may need a maintainer to approve the run. All five CI jobs should pass once released.

## Unit 10 - Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No - still awaiting review

**Summary of feedback:**
No reviewer comments had arrived on my pull request as of November 20, 2026. The PR is open and marked ready for review, and all five required CI checks (lint, typecheck, test-unit, test-integration, frontend) passed.

**How you responded:**
Not applicable yet. If comments arrive, I will respond on the PR and update this entry.

---

### Reflection

**What was harder than you expected?**
The code was not the hardest part. The process requirements were. My first PLAN.md commit was still the blank template, so it scored 0 of 8 content points in Unit 8 and I had to rewrite it with specific files, sub-tasks, risks, and edge cases. In Unit 9 I found that my branch name, feature/40-copy-link-button, did not follow CONTRIBUTING.md, which only allows fix, feat, test, docs, refactor, perf, and chore as types. I renamed it to feat/40-share-review-link and then had to update every link in JOURNAL.md that pointed to the old name. The issue was also bigger than the title I recorded in Unit 7 suggested: it said "Copy link button," but the body asked for a no-login, read-only link that expires after 30 days. That meant a migration, a model, a service, two routes, schemas, and two frontend pages.

**What did you learn about working in a large codebase?**
Contributing to someone else's project means following rules you did not write, and those rules are part of the work. CONTRIBUTING.md specified Conventional Commits with scopes, Google-style docstrings, a branch naming format, and five required CI jobs. The suite also contains 53 deliberately failing xfail tests, so "green" did not mean everything passes, and I had to check that none were tied to my issue. My feature touched about 20 files across the database migration, model, service, routes, schemas, and frontend, so I had to match existing patterns instead of inventing my own. I also hit an environment problem: macOS ignores filename case, so Git was tracking Journal.md while the assignment required JOURNAL.md. I only caught it when I read the git file list, and I had to fix it with git mv.

**How did AI tools help, and where did they fall short?**
AI was most useful for checking my work against the rubrics and CONTRIBUTING.md and explaining the Git steps for the pull request. It fell short in specific ways. It drafted PLAN.md and the PR description without seeing my code, so every file role, table name, status code, and button label had to be checked against the real files.

**What would you do differently if you started over?**
I would read CONTRIBUTING.md before creating the branch or the first commit, and I would write and commit PLAN.md before writing code. In this project my implementation commit (5225b00) added about 1,500 lines across 20 files before the reproduction commit or PLAN.md existed, so the plan ended up documenting the code instead of guiding it. I would also check the issue body against its title during Unit 7 instead of discovering the full scope later. Finally, I would open a draft PR earlier and ask for peer feedback. I did not request any on this one.

**What are you most proud of from this module?**
I am most proud of how the feature handles privacy and expiry. Expiry is enforced on the server on every request, and my tests check an expired token returning 410, invalid and empty tokens returning 404, and a link lasting exactly 30 days. The public view returns only status, overall score, sections, and expiry date, and a test confirms it leaves out the owner's email, user ID, review ID, and profile ID. I also got a full-stack change, from the migration through the UI, passing all five required CI checks on my PR.

