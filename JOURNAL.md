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