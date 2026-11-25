## Solution plan

**Issue:** [#47 — API docs don't include example `curl` commands](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47)

### Understand

**Root cause:** `docs/API.md` was written as a one-line-per-endpoint list and
was never updated when routes were added or when the request formats were
settled. It has no example invocations. Three of the routes registered in the
app aren't documented at all (`GET /`, `PUT /profiles/{profile_id}`,
`GET /reviews/{review_id}/status`).

**Expected:** A developer who has just run `make run` can copy commands from
`docs/API.md` and, in order, check that the API is up, register or log in,
capture the token, create a profile, request a review, poll its status, and
list reviews. Every route registered in `api/main.py` has a matching example
that uses the correct content type.

**Actual:** On `main`, `grep -c curl docs/API.md` returns `0`. The
non-obvious request formats are undocumented: form-encoded login with the email
sent as `username`, multipart profile creation, and the bearer-token header.
New developers have to read the route source or use Swagger to work them out.
See the reproduction notes in `JOURNAL.md` (Unit 8).

### Map

**File I'll change:**
- `docs/API.md`: the only file the fix modifies.

**Files I'll read to check that each example is correct (no changes):**
- `api/main.py`: router registration (`include_router`) and the root route
  `GET /` (line 96).
- `api/routes/auth.py`: `register` takes JSON `UserCreate`; `login` takes
  `OAuth2PasswordRequestForm`, so it needs form data, with the email in
  `username`.
- `api/routes/profiles.py`: `create_profile_endpoint` takes multipart
  `Form`/`File` with `github_username`, `portfolio_url`, and `resume_file`
  (PDF, Markdown, or plain text only, otherwise a 422).
  `update_profile_endpoint` takes JSON `ProfileUpdate`.
- `api/routes/reviews.py`: `create_review_endpoint` takes JSON
  `{"profile_id": ...}`. `list_reviews_endpoint` takes `page` and `page_size`
  (1–100, default 20). `get_review_status` is at `/reviews/{id}/status`.
- `api/routes/health.py`: currently always returns 503 (see Risks).
- `api/schemas/user.py`, `api/schemas/profile.py`, `api/schemas/review.py`:
  field names and constraints, such as the password needing 8–128 characters.
- `docs/SETUP.md`: the prerequisites list, to see whether `jq` is mentioned.

### Plan

1. **Inventory the routes.** List every route from `api/main.py` and
   `api/routes/*.py` (12 in total) and match each one to a section in
   `docs/API.md`. Add sections for the 3 missing routes. *Done when every route
   has a heading and a description line.*
2. **Add a setup block.** Put the shell variables (`BASE_URL`, `EMAIL`,
   `PASSWORD`) at the top of `docs/API.md` and note that the examples use
   `jq` to capture `TOKEN`, `PROFILE_ID`, and `REVIEW_ID`. State that `jq` is
   required, or show the raw command without it. *Done when someone can paste
   the commands from top to bottom without editing them.*
3. **Write one example per route that matches the schema.** Use JSON for
   register, profile update, and review creation; form-urlencoded data for
   login; multipart data for profile creation, with an optional
   `resume_file=@resume.pdf` variant; and `?page=&page_size=` for list. Send
   `Authorization: Bearer $TOKEN` on every protected route. *Done when each
   example matches its handler's signature.*
4. **Document the current `/health` behavior.** Say that on the current
   codebase `/health` returns 503 because of #61 and #62, and point to `GET /`
   as the reliable "is it running" check until those are fixed. *Done when a
   new developer who sees a 503 knows it's a known issue, not a mistake in
   their setup.*
5. **Run the examples against a live server.** Start the stack
   (`docker compose up -d && make setup && make run`) and run every example in
   order. Record the status codes in the PR description, then run
   `git diff --check` and `make lint`. *Done when every example returns the
   expected status.*

> Status: a first draft covering steps 1–3 is already committed on this branch
> (`13b7061`). Steps 4 and 5 are still to do in Unit 9, along with two fixes
> to the draft. First, add `jq` as a prerequisite. Second, move the
> `DELETE /profiles` example after the review examples: right now it sits at
> `docs/API.md:119`, before `POST /reviews` at line 134, so running the
> commands in order deletes the profile the review examples need.

### Inputs & outputs

- **Input:** the current `docs/API.md` (9 route lines, no examples) and the
  route handlers and schemas that define the real request formats.
- **Output:** an updated `docs/API.md` containing:
  - a setup block with variables and the `jq` note;
  - 12 route sections, each with a method, path, auth requirement, and a
    copyable `curl` command;
  - commands that chain together, so `TOKEN`, `PROFILE_ID`, and `REVIEW_ID`
    captured by earlier commands are reused by later ones;
  - a note about the current 503 from `/health`.
- **No code or behavior changes.** Routes, schemas, and responses stay the same.

### Risks & unknowns

- **`/health` is broken on `main`.** `api/routes/health.py` calls
  `db.execute("SELECT 1")` with a raw string, which fails under SQLAlchemy 2.x
  (#61), and reads `settings.redis_host`, which doesn't exist (#62). A plain
  `curl /health` example will return 503. If #61 and #62 merge before my PR,
  the note in step 4 becomes out of date, so I'll check their status before
  opening the PR.
- **The local stack doesn't match Docker.** I run the app without Docker:
  Postgres 16 is installed natively on port 5433, the port in `.env`, and
  Redis and Chroma aren't running. The app starts, login works with the seeded
  users, and `/health` returns 503 as expected. Step 5 can go ahead. Two things
  could still differ from the Docker setup reviewers use: (1) whether any
  example depends on Redis, for example if the rate limiter in
  `safety/rate_limiter.py` is wired into a route; and (2) what
  `POST /reviews` does without Chroma at `VECTOR_DB_URL`, since the background
  ingestion may fail and leave the review `failed` instead of `completed`. I'll
  note the stack I tested on in the PR description.
- **`jq` dependency.** The token- and ID-capturing commands pipe into `jq`,
  which isn't in the prerequisites table in `docs/SETUP.md`. Open question: do I
  add `jq` there, or offer a fallback with no dependencies (copy the token
  manually)? I need to decide whether touching `SETUP.md` is in scope.
- **Review flow timing.** `POST /reviews` returns `status="pending"` and runs
  ingestion and the agent as a background task (`api/routes/reviews.py:22`).
  Without a valid `OPENROUTER_API_KEY`, the review may stay pending or fail. The
  status example needs to describe what a developer will actually see.
- **Overlap with #37.** Issue #37 ("API reference doc is missing the
  `POST /profiles` request body schema") edits the same section of
  `docs/API.md`. If it merges first, I'll have a merge conflict to resolve.
- **Another claimant.** palston20 has also claimed #47, so a competing PR could
  change `docs/API.md` before mine.

### Edge cases

- **Account already exists.** Re-running the register example returns 400.
  The doc should say to switch to the login example, or use a different
  `EMAIL`.
- **Password shorter than 8 characters.** `UserCreate` returns 422, so the
  example password must be at least 8 characters.
- **Expired or missing token.** Protected routes return 401. Mention re-running
  the login example to get a new token.
- **Resume file type.** Anything other than PDF, Markdown, or plain text gets a
  422 from `POST /profiles`. The upload example should use `resume.pdf` or
  `resume.md`.
- **Profile created with no resume or GitHub username.** That's allowed (every
  field is optional), but then the review has nothing to ingest. Related to
  issue #36.
- **Pagination outside the allowed range.** `page < 1` is clamped to 1, and
  `page_size` outside 1–100 is reset to 20. Document the range so readers
  aren't surprised.
- **Order dependence.** The review examples need `PROFILE_ID`, and
  `DELETE /profiles` removes it. The delete example should come last, or warn
  that later examples won't work after it.
- **Windows / Git Bash quoting.** Use single quotes for literal strings and
  escaped double quotes only where a variable must expand inside JSON, so the
  commands also work in Git Bash.
