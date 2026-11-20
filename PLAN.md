## Solution plan

**Issue:** [Add a "Copy link" button to share a public review summary](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/40)

### Understand
Review summaries can only be viewed by a logged-in user, so there is no way to share results with someone else. The issue asks for a shareable link that opens a read-only view of a review summary without login and stops working after 30 days.

- **Expected:** An owner generates a link from the review page. Anyone with the link sees a read-only summary until the link expires.
- **Actual (on main):** The review page has no share control, and the API has no route that serves a review to an unauthenticated visitor.

I confirmed this by running the app on main and checking the review page and `api/routes/`. See the reproduction commit e339f70.

### Map
Backend:
- `core/models/review_share.py` (new): share link model holding the token, review reference, and expiry
- `alembic/versions/003_add_review_share_links.py` (new): migration for the share table
- `core/services/share_service.py` (new): creates tokens, validates them, and checks expiry
- `api/routes/share.py` (new): public route that serves a read-only review by token
- `api/routes/reviews.py`: authenticated route for creating a share link
- `api/schemas/review.py`: response schemas for share link creation and the shared view
- `api/main.py`, `core/models/__init__.py`, `core/models/review.py`: router and model registration, relationship to reviews

Frontend:
- `frontend/src/services/shareService.ts` (new): API calls for creating and fetching shared links
- `frontend/src/pages/ReviewPage.tsx`: share button, copy-to-clipboard, and confirmation message
- `frontend/src/pages/SharedReviewPage.tsx` (new): read-only view, including the expired state
- `frontend/src/App.tsx`, `frontend/src/types/index.ts`: new route and shared types

Tests:
- `tests/unit/test_share_service.py`
- `tests/unit/test_share_routes.py`
- `frontend/src/pages/__tests__/ReviewPage.test.tsx`
- `frontend/src/pages/__tests__/SharedReviewPage.test.tsx`
- `frontend/src/services/__tests__/shareService.test.ts`

### Plan
1. **Data model and migration.** Add the share link model with a unique token, a review reference, and an expiry timestamp set to 30 days after creation, and add migration 003.
2. **Service layer.** In `share_service.py`, write functions to create a link for a review the user owns and to resolve a token, returning an error for unknown or expired tokens.
3. **API routes.** Add an authenticated create route in `reviews.py` and a public read-only route in `share.py`, and register the router in `main.py`.
4. **Frontend service and UI.** Add `shareService.ts` calls, a share button on `ReviewPage.tsx` that copies the URL and shows confirmation, and `SharedReviewPage.tsx` with a route in `App.tsx`.
5. **Tests.** Cover the service, routes, and frontend components, including valid, expired, and invalid links.

### Inputs & outputs
- **Create link:** takes an authenticated user and a review ID. Returns a share URL containing the token and its expiry date.
- **View shared review:** takes a token with no authentication. Returns the read-only review summary, or a 404 or expired error response.
- **UI:** the button copies the URL and shows a "Link copied" message. The shared page renders the summary or an expired-link message.
- **Data change:** one new table of share links, added through migration 003.

### Risks & unknowns
- **Data exposure:** the public route in `api/routes/share.py` must return only the summary fields in `api/schemas/review.py`, not owner details or private fields. I need to check that the shared schema excludes them.
- **Expiry enforcement:** expiry must be checked on the server in `share_service.py` on every request, not only hidden in the UI. Comparing timestamps correctly across timezones is a possible source of bugs.
- **Auth bypass:** the public route must not sit behind the auth dependency used in `reviews.py`, and I need to confirm the authenticated create route still requires login.
- **Migration:** `alembic/versions/003_add_review_share_links.py` must apply cleanly on top of `002_add_error_message_to_reviews.py`. The revision chain is schema-only and does not depend on seeded tracker data.
- **Clipboard:** copy-to-clipboard behavior in `frontend/src/pages/ReviewPage.tsx` may differ between browsers and non-secure contexts.

### Edge cases
- An expired link (older than 30 days) shows an expired message and returns no review data.
- A malformed or nonexistent token returns a not-found response and no server error.
- A link whose review was deleted returns a not-found response and no server error (share rows cascade-delete with the review).
- A user generates a second link for the same review: `share_service.py` reuses the newest unexpired link; a new token is created only when none remain valid.
- A user tries to create a link for a review they do not own, and is rejected.
- Clipboard access fails, and the user still sees an error message in `ReviewPage.tsx`.