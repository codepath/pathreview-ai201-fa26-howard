## Solution plan

**Issue:** Review creation does not verify profile ownership, (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/67)

### Understand

The API at POST/reviews passes the authenticated user ID to the function create_review(). Despite that, review_service.py ignores that argument when creating the review. The service creates a review without checking that the profile belongs to the current user making it inconsistent with other logics in the code. Postfix the outcome should look like the user_id being used in review_services.py to authenticate the profile to the user. The expected outcome for this same request postfix returns **404 "Profile not found"** and no review is created.

### Map

**Request flow (where the bug lives):**

```
Frontend: NewProfilePage.handleProfileCreated → apiClient.createReview(profileId)
   │   frontend/src/pages/NewProfilePage.tsx, frontend/src/services/api.ts
   ▼
POST /reviews  →  create_review_endpoint            api/routes/reviews.py
   │   current_user = get_current_user (JWT)         api/middleware/auth.py
   ▼
create_review(db, profile_id, user_id)              core/services/review_service.py
   │   ✗ BUG: user_id is never used, no ownership check
   ▼
db.add(Review) / commit  →  background_tasks.add_task(process_review, ...)
```

**Files I expect to touch:**

| File | Function / area | Change |
|---|---|---|
| `core/services/review_service.py` | `create_review()` | Look up the profile by `Profile.id == profile_id` AND `Profile.user_id == user_id` before creating the review. If there's no match, raise `HTTPException(404, "Profile not found")` and don't add or commit anything. Can reuse `get_profile()` from `profile_service`. |
| `tests/unit/test_review_service.py` | `TestCreateReviewOwnership` | Remove the `xfail(strict=True, reason="issue #67 …")` marker once the fix passes. |
| `tests/unit/test_review_service.py` | 6 existing `test_create_review_*` tests | Their `mock_db_session.execute` returns an `AsyncMock` with nothing set up, so the new profile lookup will break them. Make the lookup return a profile the user owns, for example with the `make_profile_lookup_session` fixture. |
| `tests/conftest.py` | `make_profile_lookup_session`, `user_a_*` / `user_b_id` fixtures | Already added. Reuse them and edit only if needed. |
| *(maybe)* `tests/integration/` or `tests/security/` | New route test | User B sends `POST /reviews` with User A's `profile_id` and gets a 404, and no review is created. |


### Plan
Add the ownership check in create_review() (core/services/review_service.py)

Before building the Review, call get_profile(db, profile_id, user_id) from core/services/profile_service.py. That function already filters on both Profile.id and Profile.user_id.
If it returns None, raise HTTPException(status_code=404, detail="Profile not found"), so nothing is added or committed.
If it returns a profile, create the review as it does today.
Confirm the route passes the 404 through unchanged (api/routes/reviews.py)

create_review_endpoint already has except HTTPException: raise, so the 404 should reach the client as is, and the background task should never be queued.
Change nothing here unless testing shows the 404 being turned into a 500.
Update the unit tests (tests/unit/test_review_service.py)

Remove the @pytest.mark.xfail(strict=True, reason="issue #67 …") marker from test_create_review_rejects_profile_owned_by_another_user.
Fix the 6 existing test_create_review_* tests so their mock database session returns an owned profile, using the make_profile_lookup_session fixture in tests/conftest.py. They should keep testing the same thing they test now.
Run make test-unit and check that everything passes with no XPASS(strict).
Add a route-level test (tests/security/ or tests/integration/)

User B sends POST /reviews with User A's profile_id and gets a 404, with no review created.
Sending a made-up profile_id also gets a 404. Today it returns a 500 because of the foreign-key error.
User A sending their own profile_id gets a 200 with status: "pending".
Verify by hand and record the results

Run the same curl and console steps you used to reproduce the bug. User B should now get 404 {"detail":"Profile not found"}, and nothing new should appear in User A's review history.
Run make lint and make typecheck, then record the before and after results in JOURNAL.md.

### Inputs & outputs

`Inputs` - profile_id (UUID), user_id(UUID), db

`Outputs`:
| Case | Now | Postfix |
| --- | --- | --- |
| profile_id belongs to user_id |200, review with status: "pending", background task queued | No change: 200, pending review, background task queued |
| profile_id belongs to another user | 200, review created on someone else's profile, background task processes it | 404 {"detail": "Profile not found"}, no review row, no background task |

### Risks & unknowns

`Risk:`
- The 6 existing test_create_review_* tests in tests/unit/test_review_service.py will break once create_review() queries the database.
- The 404 request can turn into a 500.  If the service returned None instead of raising, the route would crash on review.id, and the generic except Exception would turn that into a 500.
`Unknown:`
- Should the 404 be raised in review_service.py (service) or in api/routes/reviews.py (route)? profile_service.get_profile() returns None and lets the route raise.
### Edge cases
 same 
#1 profile_id that doesn't exist (a valid UUID that matches no profile) this is a 500 caused by the foreign-key error. It must look identical to 404 {"detail": "Profile not found"} so nobody can tell whether another user's profile exists.
#2 Same UUID in a different format (uppercase, or no hyphens) for your own profile. The lookup must still match. 
#3 Profile the user owned but has deleted. The profile is gone, so it behaves like #2.