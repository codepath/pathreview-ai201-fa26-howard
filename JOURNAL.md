## Unit 7 — Issue selection

**Issue link:** [[Issue Link](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/67)]

**Issue title:** [Review creation does not verify profile ownership
]

**Tier:** [ ] Tier 1  [X] Tier 2  [ ] Tier 3
**Selection Notes:** I chose this issue because I understood the underlying problem of it easily. When I went to investigate where to find the bug I was able to easily point it out without the use of AI. I also believe that a tier 2 issue is perfect for me as I've worked on larger projects but not frequently enough to feel comfortable doing a tier 3 issue.

**Problem summary:**
The API at POST/reviews passes the authenticated user ID to the function create_review(). Despite that, review_service.py ignores that argument when creating the review. The service creates a review without checking that the profile belongs to the current user making it inconsistent with other logics in the code. Postfix the outcome should look like the user_id being used in review_services.py to authenticate the profile to the user.

**How to verify (bug exists → bug fixed):**
- **Reproduce today:** Log in as User A and create a profile, then log in as User B and send `POST /reviews` with User A's `profile_id`. The request should fail but doesn't: it returns 200 with a `pending` review, and the background task starts processing User A's profile.
- **Expected after the fix:** The same request returns **404 "Profile not found"** and no review is created. I chose 404 over 403 because that's what `api/routes/profiles.py` already does. Its GET, PUT and DELETE endpoints all return 404 for both "not found" and "not owned by current user", so the API never confirms that someone else's profile exists. A random `profile_id` that doesn't exist should get the same 404.
- **Tests:** I checked for an existing `xfail(strict=True)` test tied to #67 (per `docs/CONTRIBUTING.md`) and there isn't one. The existing `test_create_review_*` tests in `tests/unit/test_review_service.py` only check that `db.add` and `commit` are called. So I'll add a test where `create_review` is called with a profile the user doesn't own and should not create a review, plus a route-level test that User B gets a 404. If I find an xfail marker for #67 later, I'll remove it as part of the fix.


**Branch name:** [fix/67-review-creation-auth]

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/codepath/pathreview-ai201-fa26-howard/commit/2c70dbe79da7ec964f4a5d1304fe5343487ec207

**Reproduction summary:**
I reproduced this bug in the terminal using curl. In the terminal I logged in as both users and made a review on User B's account (token) with User A's profile ID. Instead of getting a 404 error it got a 200 ok
{"id":"2f89fded-3a6b-4615-9840-ec0108bad6b6","profile_id":"5e7a2c3f-df16-4e4a-b2dd-c91cac07a1f4","status":"pending","sections":null,"overall_score":null,"error_message":null,"created_at":"2026-11-09T08:41:54.294938Z","updated_at":"2026-11-09T08:41:54.294948Z"}

**PLAN.md link:**  https://github.com/codepath/pathreview-ai201-fa26-howard/commit/2db9665ab19746bb86735d4e1d083bb1221b86f8

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
[Anything you're still uncertain about going into Unit 9, or leave blank]

## Unit 9

### Check-in 1 (mid-week)

**Current progress:**
I added a check in `create_review()` to make sure the profile belongs to the logged-in user before creating a review. If the profile belongs to someone else or does not exist, the request returns 404 "Profile not found" without saving a review or starting background processing. The route already handles this error correctly, so it did not need changes.

I updated the existing review creation tests, removed the expected-failure marker for issue #67, and added tests for another user's profile, a missing profile, and the owner's own profile. The completed PLAN.md tasks are the ownership check, unit test updates, route tests, lint, and type checking. All 378 unit tests and 3 route tests passed, with 53 existing expected failures. The manual curl check after the fix is still pending.

**Next steps:**
Finish the manual verification from `PLAN.md`, then address any PR feedback.

**Blockers:** None.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/91

**Branch:** fix/67-review-creation-auth

**What you built:**
I fixed review creation so users can only create reviews for profiles they own. The code checks the profile ID and logged-in user's ID before saving a review. If the profile belongs to someone else or does not exist, it returns 404 "Profile not found" and does not start background processing.

**Tests added or updated:**
I updated `tests/unit/test_review_service.py` to verify that owners can create reviews and that missing profiles and profiles owned by another user raise 404 before any database write. I removed the expected-failure marker for issue #67 and updated the database mocks for the ownership lookup. I added `tests/security/test_review_creation_ownership.py` to verify that `POST /reviews` returns 200 with a pending review and starts background processing for the owner. Both rejection cases return 404 with `Profile not found`, without writing a review or starting background processing.

**Self-review confirmation:**

- [x] `make check` passes
- [x] `make test-unit` passes (378 passed, 53 expected failures)

**Draft PR feedback received from:** Kingston Davies

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [x] Yes  [ ] No

**Summary of feedback:**
Kingston Reviewed my PR in person and let me know I should make my PR clearer so that someone with no knowledge of what I was doing could easily latch on

**How you responded:**
I edited my PR comment to be more comprehensive of what I did

---

### Reflection

**What was harder than you expected?**
Navigating the codebase was a bit harder than I expected. This codebase was actually the size of a real large codebase which I was not expect so finding what files effected my issues and trying to make sure I wasn't spilling on to other issues was a big concern.

**What did you learn about working in a large codebase?**
I learned that in a large codebase it helps to check how the rest of the app handles the same problem before deciding what to do. I looked at `api/routes/profiles.py` and saw that it returns a 404 when the profile belongs to someone else, so I used the same response for review creation. I also learned that PRs have to explain your changes clearly enough for someone who hasn't been working on the issue.

**How did AI tools help — and where did they fall short?**
It helped the most in navigating the codebase. Since the codebase was so large and my issue was so small, it wouldve taken me hours to find all the little connections to this issue and figure out how to reproduce it on my own. This is where AI helped the most. I wouldnt consider this a shortfall on AIs part but I did experience a lack of credits toward the end which made me have to start using my prompts more wisely

**What would you do differently if you started over?**
If I were to start over I think I'd pick a more challenging issue. Fixing issue #67 gave me more confidence because I figured out where the ownership check belonged and tested it in both `create_review()` and the `POST /reviews` route.

**What are you most proud of from this module?**
I was most proud of making `PLAN.md` because I had to find the affected files and explain the issue back to myself before I could map out the fix. One part I'm proud of was planning to test both a missing profile and one that belonged to another user, since both were supposed to return the same 404. It reminded me of what I was doing during my internship.
