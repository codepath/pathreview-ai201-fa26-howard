# Module 3 Journal

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47

**Issue title:** API docs don't include example `curl` commands

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The API reference in `docs/API.md` lists PathReview's endpoints (health, auth,
profiles, reviews), but it never shows how to actually call them. A new
contributor who has just started the backend has no copy-and-paste way to check
that the API works, log in, or carry a token and IDs from one request to the
next. Some routes in `api/routes/` are also missing from the doc entirely, such
as the root route, profile update, and review status. A successful fix adds
working `curl` examples for every route registered in `api/main.py`. Those
examples will cover the bearer-token flow and the correct request formats (JSON,
form-encoded login, multipart resume upload), so a first-time developer can
smoke-test the whole API from the terminal. The change only touches
documentation, so API behavior stays the same.

**Branch name:** `docs/47-api-curl-examples`

**Setup confirmation:** [x] App runs locally at localhost:5173 (native Postgres 16 on port 5433 instead of Docker)

**Cohort ledger:** [x] Issue added to cohort ledger

### Selection notes — "Is this right for me?" checklist

**Part 1 — Understanding the issue**
- [x] *Can I explain it in my own words?* The API doc describes the endpoints
  but doesn't show how to call them, so a new developer can't quickly confirm
  the API works. When it's done, every endpoint will have a runnable `curl` command.
- [x] *Which part of the app?* The labels are `docs` and `good first issue`. The
  only file to change is `docs/API.md`. The source of truth for checking the
  examples is `api/main.py` and `api/routes/` (auth, profiles, reviews, health).
- [x] *What does "done" look like?* Before: `docs/API.md` has route
  descriptions and no examples, and a few routes aren't documented. After: an
  environment-variable setup block (`BASE_URL`, `TOKEN`, `PROFILE_ID`,
  `REVIEW_ID`) and one copyable `curl` command per route that matches the real
  request schema.

**Part 2 — Tier fit**
- [x] This is my first contribution to a large codebase, so I chose Tier 1. The
  change stays inside one file and doesn't require understanding the RAG or
  agent pipeline.

**Part 3 — Codebase readiness**
- [x] *Found the specific code:* I read each route handler in `api/routes/` and
  the request schemas, so I know which endpoints take JSON, which take form
  data (`/auth/login`), and which take multipart data (profile creation with a
  resume upload).
- [x] *Understand the surrounding code:* I wrote a plan (`PLAN.md`) before
  editing. Because this is a docs-only change, it can't break runtime behavior.
  The main risk is examples that don't match the real routes, so I'm checking
  each example against its handler.
- [x] *Read the relevant tests:* No unit test covers `docs/API.md`. For this
  issue, the checks are `git diff --check`, `make lint`, and a manual check that
  every route in `api/main.py` has an example. I read
  `tests/unit/test_security.py` end-to-end to see how the test suite uses
  fixtures and assertions, even though my change doesn't need a new test.

**Part 4 — Scope and time**
- [x] *Others on this issue:* Besides me, one other student (palston20) has
  commented to claim it. Claims are non-exclusive and my grade comes from my
  own work, so I'm fine with that.
- [x] *Realistic for Units 8–9:* The issue estimates 2–3 hours, and a first
  draft is already on my branch. That leaves enough time to review it and
  revise it after feedback.
- [x] *Blockers:* There are none. The issue doesn't depend on any other
  unresolved issue.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/corr18/pathreview-ai201-fa26-howard/commit/0bfbbc61a196169c8a9cce581eafb7061a0a5f8f

**Reproduction summary:**
I compared `docs/API.md` on `main` with the routes registered in `api/main.py`
and `api/routes/*.py`. The doc has zero `curl` examples, leaves out 3 of the 12
routes (`GET /`, `PUT /profiles/{id}`, `GET /reviews/{id}/status`), and never
explains the form-encoded login, multipart profile upload, or bearer-token
requirements. I also found that `GET /health` currently always returns 503
because of #61 and #62.

**PLAN.md link:** https://github.com/corr18/pathreview-ai201-fa26-howard/blob/docs/47-api-curl-examples/PLAN.md

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:**
- I still need Docker (or Colima) running locally so I can run every example
  against a live server (PLAN.md step 5).
- Should `jq` be added to the prerequisites in `docs/SETUP.md`, or should the
  examples include a fallback that doesn't need it?
- How should the docs handle the `/health` 503 if #61 and #62 haven't merged
  by the time I open my PR?

### Reproduction steps (issue #47)

Issue #47 is a documentation gap, so I reproduced it by checking what
`docs/API.md` on `main` provides against the routes the API actually
registers.

1. Count the `curl` examples in the API reference on `main`:

   ```bash
   git show main:docs/API.md | grep -c curl
   # 0
   ```

2. List the routes that the doc covers (9 lines, with no example invocations):

   ```bash
   git show main:docs/API.md | grep -E '^`(GET|POST|PUT|DELETE) '
   # GET /health, POST /auth/register, POST /auth/login,
   # POST /profiles, GET /profiles/{profile_id}, DELETE /profiles/{profile_id},
   # POST /reviews, GET /reviews/{review_id}, GET /reviews
   ```

3. List the routes the app actually registers (12):

   ```bash
   grep -nE '@app\.get' api/main.py
   grep -nE '@router\.(get|post|put|delete)' api/routes/*.py
   grep -nE 'APIRouter\(prefix' api/routes/*.py
   ```

   The result: `GET /`, `GET /health`, `POST /auth/register`, `POST /auth/login`,
   `POST /profiles`, `GET /profiles/{id}`, `PUT /profiles/{id}`,
   `DELETE /profiles/{id}`, `POST /reviews`, `GET /reviews/{id}`,
   `GET /reviews`, `GET /reviews/{id}/status`.

**What I observed:**
- `docs/API.md` has **zero** `curl` commands. A new developer has no
  copy-and-paste way to smoke-test the API.
- **3 of the 12 routes aren't documented at all:** `GET /`
  (`api/main.py:96`), `PUT /profiles/{profile_id}`
  (`api/routes/profiles.py:146`), and `GET /reviews/{review_id}/status`
  (`api/routes/reviews.py:139`).
- The doc never mentions how requests have to be formatted, and those formats
  aren't guessable:
  - `POST /auth/login` takes **form data** (`OAuth2PasswordRequestForm`) with
    the email sent as `username`, not JSON (`api/routes/auth.py`).
  - `POST /profiles` takes **multipart form data** (`Form(...)` / `File(...)`),
    not JSON (`api/routes/profiles.py:23`).
  - Every profile and review route needs an `Authorization: Bearer <token>`
    header.
- A related problem turned up while reproducing: `GET /health` on `main`
  always reports `postgres` and `redis` as unhealthy and returns **503**. That
  happens because of `db.execute("SELECT 1")` with a raw string (issue #61) and
  `settings.redis_host`, which doesn't exist (issue #62), both in
  `api/routes/health.py`. A health `curl` example has to account for this.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
All five PLAN.md sub-tasks are done:
- Steps 1–3 (route inventory, setup block, one `curl` example per route) were
  already in my first draft.
- Step 4: in `1bbfa75` I documented the known `/health` 503 (#61, #62). I also
  fixed the two draft problems I found in Unit 8. The `DELETE /profiles`
  example now comes last, because deleting a profile also deletes its reviews,
  so the review examples returned `404` after it. `jq` is now documented, with
  a fallback for anyone who doesn't have it.
- Step 5: I ran every example in order against my local server. All 12 routes
  returned the expected status codes.
- I added `tests/unit/test_api_docs.py`. It checks `docs/API.md` against the
  app's OpenAPI schema, so a new or renamed route without a doc example fails
  the test. I confirmed that it fails against `main`'s original doc and
  against my old draft's ordering.

**Next steps:**
- Open a draft PR and ask for peer review in the cohort Slack channel.
- Address the feedback, confirm all five CI jobs are green on the PR, then mark
  it ready for review.

**Blockers:**
None. One thing to watch: #37 (PR #107) also edits `docs/API.md`, so whichever
merges second will need to resolve a merge conflict.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/82

**Branch:** `docs/47-api-curl-examples`

**What you built:**
I rewrote `docs/API.md` so every one of the 12 registered routes has a
copy-and-paste `curl` example. The examples are ordered to run top to bottom:
they capture the token and the profile and review IDs, and reuse them in later
commands. The doc also covers the known `/health` 503, the `jq` prerequisite,
and the error responses readers are likely to hit. A new unit test compares
the doc with the app's OpenAPI schema, so a route added without an example
fails CI.

**Tests added or updated:**
I added `tests/unit/test_api_docs.py`, with 4 tests. They check that:
- the doc covers exactly the routes in the app's OpenAPI schema;
- each example uses `curl` with the right HTTP method;
- only the protected routes' examples send the bearer token;
- the delete example comes after every example that reuses its IDs.

All four fail against `main`'s original doc, and the ordering test fails
against my earlier draft. No xfail marker was tied to #47, so I didn't delete
any.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** a cohort peer (Slack). They asked me to
organize the work better and make the solution more concise. In response
(`83d67b2`) I:
- restructured `docs/API.md` around an endpoint summary table, a single
  quick-start section (variables, `jq`, common errors), and short examples
  grouped by area, which cut it from 203 to 140 lines;
- folded the docs test from 6 checks into 4.

I re-ran every example against the local server and re-ran `make check` and
`make test-unit`.

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No maintainer or instructor review has come in on
[PR #82](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/82).
The only comment on the PR is my own review request, posted after I addressed
the Slack peer feedback in Unit 9. That feedback ("organize it better, make the
solution more concise") is documented in Check-in 2.

**How you responded:**

---

### Reflection

**What was harder than you expected?**
Getting the environment running was harder than the fix itself. `make setup`
assumes Docker, and I didn't have it, so I ran Postgres 16 natively on the
port `.env` expects. I also had to work out which services the API actually
needs to start: Postgres, but not Redis or Chroma. The second surprise was
that a docs issue still needed real verification. Reading the handlers wasn't
enough. Only running every example in order showed that the
`DELETE /profiles` example sat before the review examples. Deleting a profile
also deletes its reviews, so every command after it returned `404`. I also
didn't expect other seeded bugs to affect my issue: `/health` returns `503`
because of #61 and #62, so the doc had to warn readers instead of showing a
"healthy" example.

**What did you learn about working in a large codebase?**
In someone else's project, the code is the source of truth, not the existing
docs. I checked each example against the route handler and schema it calls,
for example login takes form data with the email as `username`, not JSON. I
learned to keep my change narrow. I put the `jq` note in `docs/API.md`
instead of also editing `SETUP.md`, so the PR stayed reviewable. I also
noticed that #37 / PR #107 edits the same file, so I flagged the likely merge
conflict for reviewers. The project's conventions (branch names,
Conventional Commits, the PR template, five required CI jobs, xfail markers
tied to issues) felt like overhead at first. Once I used them, I saw they're
what let many contributors work in parallel without breaking `main`.

**How did AI tools help — and where did they fall short?**
AI was most useful for mapping the codebase quickly: listing every
registered route, comparing that list with the doc, and running all the
examples with their status codes. It also wrote the docs test that keeps
`docs/API.md` in sync with the routes. It fell short in a few ways:
- Its first version of the test assumed FastAPI lists every route in
  `app.routes`. On this FastAPI version, included routers are wrapped, so the
  test was wrong. That only showed up when we ran it against the old versions
  of the doc, and it was rewritten to read the OpenAPI schema instead.
- It couldn't do anything outside the terminal: installing Docker was blocked,
  and it had no access to the cohort ledger sheet or Slack.
- It couldn't decide what my peer's vague feedback meant. I had to choose how
  to read "organize it better."

My takeaway is that I need to understand and check what the AI produces,
because it can be confidently wrong.

**What would you do differently if you started over?**
I'd follow the process in order. My first draft and PR (Nov 11) came before
I had reproduced the issue, written a real plan, or run the app. That's
exactly why the ordering bug and the missing `/health` warning got through.
I'd open the PR as a draft and keep it there until I had feedback. I'd also
ask my peer to clarify vague feedback instead of guessing. And I'd keep the
commit history cleaner, since journal-only commits are mixed in with the
actual fix.

**What are you most proud of from this module?**
The `tests/unit/test_api_docs.py` test. Instead of only fixing the docs once,
it makes CI fail if anyone adds a route without documenting it, or puts the
cleanup example in the wrong place. I checked that it catches both the
original problem on `main` and my own earlier mistake, which makes me
confident the fix will last.
