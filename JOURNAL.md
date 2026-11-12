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
