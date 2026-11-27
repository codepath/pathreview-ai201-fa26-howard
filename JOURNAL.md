# JOURNAL

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/72

**Issue title:** `verify_password` raises `UnknownHashError` on malformed stored hashes instead of returning False

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The `verify_password` function in `core/security.py` checks a user's password against the hash stored for them, using passlib. If a stored hash is corrupted or in a format passlib doesn't recognize, passlib throws an `UnknownHashError` and the function lets it bubble up instead of handling it. That means a bad record in the database can crash a login attempt rather than just rejecting it. A successful fix catches that error and returns `False`, so verification fails closed and the user is simply not authenticated. The fix also removes the `xfail` marker (H-05) on the matching test in `tests/unit/test_security.py`, so that test has to actually pass.

**Branch name:** fix/72-verify-password-malformed-hash

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

**Selection notes ("Is this right for me?" checklist):**
- Scope is small and contained: one function in one file, plus removing one test marker.
- The expected behavior is clearly defined (return `False` instead of raising), so I know what "done" looks like.
- There's already a test covering it, so I can confirm the fix by running `pytest tests/unit/test_security.py`.
- I'm comfortable with Python exception handling, and I'll need to read up on how passlib raises `UnknownHashError`.
- Estimated at 1 to 2 hours, which fits well within the Unit 8 to 9 timeline and leaves room to start a second issue.
## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/kwesi115/pathreview-ai201-fa26-howard/commit/60563d1eabe4a4eee0c3555d50ba582a59a856b1

**Reproduction summary:**
I reproduced the bug by running the xfail test with `--runxfail` and by calling `verify_password` directly with a malformed hash, and both times passlib raised `UnknownHashError: hash could not be identified` instead of returning False. I also found that a truncated bcrypt hash raises a plain `ValueError` (not `UnknownHashError`), so the fix has to cover that case too.

1. `pytest tests/unit/test_security.py -k wrong_hash_format -v` shows `XFAIL` (1 xfailed, 24 deselected).
2. `pytest tests/unit/test_security.py -k wrong_hash_format -v --runxfail` fails:
   ```
   >           raise exc.UnknownHashError("hash could not be identified")
   E           passlib.exc.UnknownHashError: hash could not be identified

   .venv\Lib\site-packages\passlib\context.py:1132: UnknownHashError
   FAILED tests/unit/test_security.py::TestSecurity::test_verify_with_wrong_hash_format
   ```
3. `python -c "from core.security import verify_password; verify_password('password', 'not_a_valid_bcrypt_hash')"` raises:
   ```
   File ".venv\Lib\site-packages\passlib\context.py", line 1132, in identify_record
     raise exc.UnknownHashError("hash could not be identified")
   passlib.exc.UnknownHashError: hash could not be identified
   ```
4. Other malformed hashes (passlib 1.7.4, bcrypt 4.3.0):
   ```
   ''                  -> passlib.exc.UnknownHashError: hash could not be identified
   '$2b$12$short'      -> ValueError: salt too small (bcrypt requires exactly 22 chars)
   '$argon2id$v=19$xx' -> passlib.exc.UnknownHashError: hash could not be identified
   ```
5. In `api/routes/auth.py`, `login()` calls `verify_password` on line 80. The error is not an `HTTPException`, so the generic `except Exception` catches it and the user gets a 500 "Login failed" instead of a 401.

**PLAN.md link:** https://github.com/kwesi115/pathreview-ai201-fa26-howard/blob/fix/72-verify-password-malformed-hash/PLAN.md

**Walkthrough video (recommended):** Not recorded

**Blockers or open questions:**

- Should I catch all `ValueError` or only `UnknownHashError`? Catching only `UnknownHashError` misses the truncated bcrypt hash (`$2b$12$short`), which raises a plain `ValueError`. But `ValueError` is broader and could hide other problems.
- Which commit scope should I use for the fix? The code is in `core/`, but `core` isn't in the scope list in CONTRIBUTING.md. I used `api` for the docs commits since the impact is on the login route, but I'm not sure that's right for the actual code change.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:** All five sub-tasks in PLAN.md are done. `verify_password` now catches `ValueError` (which covers `UnknownHashError`) and returns `False`, and it logs a warning with only the error type, never the hash. I updated the docstring, removed the strict xfail marker from `test_verify_with_wrong_hash_format`, and added tests for an empty hash, a truncated bcrypt hash and an argon2-style hash. `make check` passes and `make test-unit` gives 379 passed, 52 xfailed, no XPASS.

**Next steps:** Get my draft PR reviewed in Slack, address any feedback, confirm all five CI jobs are green, then mark the PR ready for review.

**Blockers:** None right now. The pre-commit black hook got blocked once by a Windows Application Control policy, but it passed when I ran it again.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/83

**Branch:** `fix/72-verify-password-malformed-hash`

**What you built:** I fixed `verify_password` in `core/security.py` so it catches `ValueError` (which covers passlib's `UnknownHashError`) and returns False instead of crashing on malformed or unrecognized stored hashes. It logs a `password_verify_malformed_hash` warning with only the error type, never the hash or password. Because of this, a login with a corrupted hash now gets a normal 401 instead of a 500. I also updated the docstring to match.

**Tests added or updated:** In `tests/unit/test_security.py` I removed the strict xfail marker from `test_verify_with_wrong_hash_format` and added `test_verify_with_empty_hash`, `test_verify_with_truncated_bcrypt_hash` and `test_verify_with_unsupported_scheme_hash`. All four pass, and the existing `test_verify_password_correct` still passes, so a valid hash with the right password still returns True.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes (I ran both before opening the PR: `make check` was clean and `make test-unit` gave 379 passed, 52 xfailed, no XPASS. All five CI jobs on the PR are green too.)

**Draft PR feedback received from:** Brian

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
As of 11/26 there are no reviews or comments on PR #83 from reviewers or maintainers. All five CI jobs are still green and the PR is open and marked ready for review. The only feedback so far was the draft PR check from Brian in Slack that I noted in Unit 9.

**How you responded:**


---

### Reflection

**What was harder than you expected?**
The code fix itself was about five lines. What took longer was everything around it. My first plan was to catch only `UnknownHashError`, because that's what the issue named. When I actually tested different bad hashes, a truncated bcrypt hash like `$2b$12$short` raised a plain `ValueError` instead, so that plan would have left a crash in place. I also didn't expect the strict xfail marker to make CI fail the moment my fix worked. The tooling on Windows was another surprise: `make` wasn't installed, the seed script crashed trying to print a check mark to the console, and the pre-commit black hook got blocked once by Windows Application Control. Finally, I opened my PR against my own fork's `main` by accident (PR #1) before I got the right one into codepath's `main` (PR #83).

**What did you learn about working in a large codebase?**
In my own projects I just change whatever I want. Here I had to follow conventions that already existed: the commit format from CONTRIBUTING.md, the `structlog.get_logger()` pattern used in `api/routes/health.py`, and the style of the existing tests in `TestSecurity`, which is why I wrote three separate test methods instead of one parametrized test. I also learned to look at the callers before changing something. Reading `api/routes/auth.py` showed me the real impact: the generic `except Exception` turned a bad hash into a 500 instead of a 401. And I learned to keep the diff small. CONTRIBUTING warns against bulk-fixing lint, so I only touched `core/security.py` and its test file.

**How did AI tools help — and where did they fall short?**
I used Claude Code for this module. It was most useful for the repetitive parts: running the reproduction commands, trying the malformed hashes one by one, running `make check` and `make test-unit` after each step, and filling in the PR template. It also caught the truncated bcrypt case while testing edge cases, which changed my plan. Where it fell short, I had to step in. It couldn't log in to the GitHub CLI for me, because I had to approve that in my browser. It also didn't know my course rubric, so the first submission came back incomplete: the journal fields ran together when GitHub rendered them, and I had submitted a PR link when the portal wanted the branch link. Decisions like catching `ValueError` versus only `UnknownHashError`, and what is safe to log, were mine to check and own.

**What would you do differently if you started over?**
I would read the full rubric and the portal instructions before starting, so I'd know from day one that I submit the branch URL and how each journal field needs to look. I'd comment on issue #72 to claim it right away, because I never did, and another student later commented that they were working on it. I'd set up my Windows tools (make, gh) in the first week instead of finding out mid-unit. And I'd ask for a review on the PR itself earlier, so there would be feedback on GitHub to respond to this week.

**What are you most proud of from this module?**
Testing the edge cases before writing the fix. Trying the empty string, the truncated bcrypt hash and the argon2 hash showed me that catching only `UnknownHashError` wasn't enough. Because of that, the fix handles every malformed input I tried, and each case has its own test.
