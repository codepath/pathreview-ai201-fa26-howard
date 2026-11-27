## Unit 7 — Issue selection

**Issue link:** [Issue Link](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/26)

**Issue title:** Add a safety event count to the health check endpoint
 

**Tier:** [X] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The issue seems to be that there is an existing function that records the count of safety events. I would have to connect that actually to the safety layer so that it gets implemented into the program and reports the safety event count. I must look through the files: api/routes/health.py and safety/monitoring.py for connecting these two areas together. 

**Branch name:** feat/26-safety-event-health-check

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger


Using the "Is This Issue Right for Me?" Checklist

Part 1 — Understanding the Issue

Can I explain what this issue is asking for in my own words?

Paraphrase the issue without looking at it. If you can't, you don't understand it well enough yet. Read the full issue body, look at any linked PRs or comments, and try again.

[X] I can explain the problem and the expected behavior in 2–3 sentences without reading the issue.

Do I understand which part of the app is affected?

Check the labels on the issue — they often indicate the area (api, rag, ingestion, frontend, etc.). Look at the referenced files if any are mentioned. Find those files in the repo.

[X] I've located the relevant files and confirmed they exist in the codebase.

Do I understand what "done" looks like?

Can you describe what the app should do (or not do) once the issue is fixed? If the issue has acceptance criteria, read them carefully. If it doesn't, try writing your own — that forces you to understand the scope.

[X] I can describe a concrete before-and-after: what the user sees before the fix and what they see after.

Part 2 — Tier Fit
Issues in the tracker are tagged with a tier level. Here's what each one means:

| Tier | Description | Typical scope |
|---|---|---|
| Tier 1 | Self-contained, localized fix. The change lives in one or two files and doesn't require understanding how the whole system fits together. | Bug fix, missing validation, broken test, documentation update |
| Tier 2 | Requires understanding how two or more modules interact. May involve a service layer, database model, or API endpoint. | Feature addition, refactor, data flow bug |
| Tier 3 | Requires understanding the full system — multiple modules, possibly infrastructure or AI pipeline changes. | Architecture change, cross-cutting behavior, RAG or agent modification |

Is the tier a realistic match for where I am right now?

[X] If this is my first open source contribution: I'm choosing Tier 1.
[ ] If I've contributed to large codebases before: Tier 2 or 3 is fair game.
[ ] I'm not choosing a Tier 3 issue to "challenge myself" if I haven't completed a Tier 1 or 2 first — scope surprises in Unit 9 don't have a safety net.

Part 3 — Codebase Readiness
Can I find the relevant code?

Before claiming the issue, locate the specific function, route, or module it describes. Don't rely on grep alone — open the file, read the surrounding context, and confirm you're in the right place.

[X] I've found and read the specific code the issue references (not just the file — the function or section).

Do I understand the surrounding code well enough to change it safely?

You don't need to understand the whole codebase. But you need to understand the file you're about to edit well enough to predict what a change will break. Read the function signatures, docstrings, and any callers.

[X] I've read enough surrounding context that I can write a rough plan for the fix without looking anything up.

Have I read the relevant test file?

Find the test file for the module your issue touches (tests/unit/ is the right place to start). Look at how existing tests are structured — fixtures, assertions, mock patterns. You'll need to write at least one new test.

[X] I've found the test file for my module and read at least one test end-to-end.

Part 4 — Scope and Time
How many others are already working on this issue?

Claims are non-exclusive — more than one student may work on the same issue, and your grade comes from your own artifacts, never from being first. Still, check the issue comments and the Claims column in the Issue Catalog tab of the cohort ledger: a less-crowded issue of the same tier can mean smoother coaching and peer review.

[X] I've checked the issue comments and the ledger's Claims count, and I'm fine with how many others are on this issue.

Is the scope realistic for Units 8–9?

You have roughly two weeks to implement, test, and submit a PR. Tier 1 issues typically take 2–4 hours of focused work, up to 5. Tier 2 issues typically take 4–6 hours, up to 8. Tier 3 issues typically take 7–10 hours, up to 12.

Think about your week — other classes, work, other commitments. Is this achievable?

[X] I've estimated the time this will take and I'm confident I can complete it before the Unit 9 deadline.

Are there any blockers or dependencies?

Some issues say "blocked by #X" or reference another issue that needs to be resolved first. Check the issue for any such dependencies.

[X] This issue has no open blockers or dependencies on other unresolved issues.
Verdict
If you checked every box, you're ready to claim the issue. If any box is unchecked:

Unchecked item in Part 1: Spend 15 more minutes reading the issue and the relevant code before deciding.
Unchecked item in Part 2: Consider a lower tier. There's no shame in a well-executed Tier 1 over a half-finished Tier 2.
Unchecked item in Part 3: Do one more codebase exploration session (see the codebase navigation guide) before committing.
Unchecked item in Part 4: Choose a different issue, or negotiate the timeline with your instructor.
Once you've checked all boxes: comment on the issue, add it to the cohort ledger, and start Unit 7.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** [link to commit documenting the reproduced issue](https://github.com/codepath/pathreview-ai201-fa26-howard/commit/f309116322b948f32245fbfb7921f9e947997232)

**Reproduction summary:**
[1–2 sentences: How did you reproduce the issue? What did you observe?]
When running this command `curl http://localhost:8000/health`
safety_events_last_hour is 0

Then I incremented the counter by hand with this command 
`docker compose exec redis redis-cli INCR safety:events:pii_detected`
C:\Users\Nkiru\AI201\fall26pathreview\pathreview-ai201-fa26-howard\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
(integer) 2

So safety_events_last_hour should be 2

But running the curl command again:
safety_events_last_hour is still 0

This is where our bug lies. 

**PLAN.md link:** [link to PLAN.md in your fork](https://github.com/Dani-risingBW/pathreview-ai201-fa26-howard/blob/feat/26-safety-event-health-check/PLAN.md)

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
[Anything you're still uncertain about going into Unit 9, or leave blank]

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Nothing yet. Just worked on reproducibility again. 

**Next steps:**
Fixing the health check and connecting the saftey counter. 

**Blockers:**
None

---

### Check-in 2 (end of week)

**PR link:** [PR #110](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/110)

**Branch:** feat/26-safety-event-health-check

**What you built:**
The `/health` endpoint now reports the real number of safety events instead of always saying 0. It creates a `SafetyMonitor` from the Redis client and adds up `get_event_count()` for every event type in `VALID_EVENT_TYPES`, but only when Redis is healthy. I also fixed the Redis connection to use `settings.redis_url`, since `redis_host` didn't exist (issue #62), and removed #62's mypy suppression from `pyproject.toml`.

**Tests added or updated:**
I added `tests/unit/test_health.py`, which uses a mocked Redis and database. It covers four cases:
- all dependencies healthy
- Redis down: the endpoint returns a 503 and the safety count stays 0
- the safety count is summed across all event types
- `log_event()` increments the right Redis key

**Self-review confirmation:** [X] make check passes  [X] make test-unit passes

**Draft PR feedback received from:** none


## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [X] No — still awaiting review

**Summary of feedback:**
No review has come in yet. PR #110 is open with all five CI checks passing (lint, typecheck, test-unit, test-integration, frontend), and there are no reviews or comments so far.

**How you responded:**


---

### Reflection

**What was harder than you expected?**
Getting the environment running was harder than the fix itself. Docker Desktop kept not running or not being on my PATH in Git Bash, so `docker` was "command not found." My other projects' Vite servers were using port 5173, so for a while localhost:5173 showed a different app. The Postgres and Redis containers also stopped whenever Docker restarted. Writing the tests was harder than I expected too. I had to learn that `health_check()` *raises* an `HTTPException` when something is unhealthy instead of returning a value, so the test needed `pytest.raises`. I also had to learn that a mock with `return_value = "5"` answers every key, so five event types added up to 25, not 5.

**What did you learn about working in a large codebase?**
A small issue can be connected to other issues. My fix for #26 needed a working Redis client, and that turned out to be a separate seeded bug (#62), which I only found because `pyproject.toml` had a comment about it. I learned to read the contributing rules: removing a bug's mypy suppression or xfail marker is part of fixing it, and baseline cleanups belong in their own PR. I also learned to keep my scope narrow. The Postgres `SELECT 1` bug (#61) was right next to my code, but I left it alone and explained it in my PR instead of fixing everything I saw.

**How did AI tools help — and where did they fall short?**
AI was most useful for explaining code I didn't understand yet. Examples were how `redis_url` gets loaded from `.env`, why I couldn't import a method like `get_event_count` directly, and what each test failure actually meant. It also helped with setup, linting, and writing a PR description with real before/after output. It fell short in a few places. At one point it said the app was running on 5173 when another app had taken the port, and it had to correct itself. The servers it started in the background kept getting killed, so I ran commands like the `redis-cli` reproduction myself. It also couldn't see my course rubric, so decisions about scope, what goes in the PR, and opening it as final instead of a draft had to come from me.

**What would you do differently if you started over?**
I would read `pyproject.toml` and CONTRIBUTING.md during planning, so I'd have found the overlap with #62 in my PLAN.md instead of right before opening the PR. I would make sure Docker was installed, running, and on my PATH before starting anything else. I would also write the failing test first and use it as my reproduction commit, so my git history shows the bug failing and then passing.

**What are you most proud of from this module?**
Reproducing the bug myself. I recorded safety events directly in Redis with `redis-cli INCR`, then showed that `/health` still reported 0. After the fix, the same data showed `"safety_events_last_hour":3` and Redis reported as healthy. That gave me clear proof the bug was real and that my change fixed it.