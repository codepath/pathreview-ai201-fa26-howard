# Solution plan for PathReview issue #72

- **Issue:** [Malformed stored password hashes raise instead of returning False](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/72)
- **Branch:** `fix/72-malformed-password-hashes`
- **Prepared:** November 25, 2026 (America/New_York)
- **Stage:** Unit 9. Implementation, local validation, and PR CI verification are complete.
- **Pull request:** [Howard PathReview #113](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/113)
- **Execution status:** All five plan tasks are complete. The 37 affected tests pass, `make check` passes, the unit suite reports 388 passed / 52 xfailed, and all 18 frontend tests pass. All five CI jobs passed in [run 45716211881](https://github.com/codepath/pathreview-ai201-fa26-howard/actions/runs/45716211881), and PR #113 was marked ready for review. The [PR checks](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/113/checks) track the latest commit.
- **Reproduction commit:** [18fcce3](https://github.com/shreejaysubedi/pathreview-ai201-fa26-howard/commit/18fcce31ea1b7e84ea5951d603830b2a7af1a491)
- **Evidence:** [Commands and observed output](docs/evidence/unit8-reproduction.txt)

## 1. Understand

Before the fix, `core/security.py::verify_password()` immediately returned `bool(pwd_context.verify(...))`. If Passlib could not identify or parse the stored hash, it raised before `bool()` could produce a result. The helper did not catch that error, so `api/routes/auth.py::login()` reached its generic exception handler and responded with HTTP 500. The implementation now catches `ValueError` around that comparison and returns `False`.

At the reproduction stage, `TestSecurity.test_verify_with_wrong_hash_format` expected `False` for `not_a_valid_bcrypt_hash`, but carried a strict `xfail` marker for issue #72 / manifest H-05. Running it with `--runxfail` reproduced `UnknownHashError` and exit code 1. The unchanged security test file then reported 24 passed and 1 xfailed. The implementation expands that case to four hashes and removes its marker.

The required outcome is a failed verification (`False`) for malformed stored hash strings. Valid bcrypt hashes must continue to return `True` for the matching password and `False` for an incorrect password. The login route should consequently use its existing HTTP 401 invalid-credentials response.

Local investigation also found that an empty or unrecognized stored hash raises `UnknownHashError`, while `$2b$12$invalid` raises `ValueError` because its salt is too short. The installed `UnknownHashError` is a subclass of `ValueError`. Passlib's [exception reference](https://passlib.readthedocs.io/en/stable/lib/passlib.exc.html#passlib.exc.UnknownHashError) and [verification reference](https://passlib.readthedocs.io/en/stable/lib/passlib.context.html#passlib.context.CryptContext.verify) describe this exception family. This supports catching `ValueError` around the verification call, rather than handling only unrecognized prefixes.

## 2. Map

- **Implementation target:** `core/security.py::verify_password()` and its return-value docstring. `pwd_context` is configured for bcrypt in this module.
- **Existing regression and controls:** `tests/unit/test_security.py::TestSecurity`, especially `test_verify_with_wrong_hash_format`, `test_verify_password_correct`, `test_verify_password_incorrect`, `test_verify_password_case_sensitive`, and `test_hash_password_long_input`.
- **Caller:** `api/routes/auth.py::login()` passes `form_data.password` and `user.hashed_password` to the helper. Its `False` branch raises HTTP 401, and its generic handler raises HTTP 500.
- **Stored value:** `core/models/user.py::User.hashed_password` is a non-nullable string column. Empty and corrupt string contents are the relevant boundary cases.
- **Request boundary:** The login route uses FastAPI's `OAuth2PasswordRequestForm`. `api/schemas/user.py::UserCreate` defines registration validation separately; this fix targets verification.
- **Caller tests:** `tests/unit/test_auth.py` covers isolated login-route behavior using a mocked database dependency and the real security helper.
- **Required validation commands and CI definitions:** `Makefile` and `.github/workflows/ci.yml`.

The relevant path is: login form data, user lookup, `verify_password()`, Passlib comparison, then the route's existing authentication response. The proposed implementation change belongs in the shared helper because the caller already handles a `False` result.

## 3. Plan

1. **Extend regression coverage before the fix.** Parameterize the existing malformed-hash test with a non-hash string, an empty string, an unsupported hash-like string, and a truncated bcrypt string. Keep its issue-specific `xfail` marker until the implementation passes. Use `--runxfail` on this specific test to confirm the failing behavior of the new cases.
2. **Handle invalid verification values in the helper.** Wrap only `pwd_context.verify(plain_password, hashed_password)` in `try` / `except ValueError`, returning `False` on that exception family and preserving the normal boolean result. Update the docstring to describe malformed-hash rejection. Avoid `except Exception`, changes to password hashing, or changes to the configured bcrypt scheme.
3. **Activate the regression tests and protect normal behavior.** Remove the strict `xfail` marker associated with issue #72 once all malformed-hash cases pass. Retain the existing correct-password, incorrect-password, whitespace, special-character, and long-input controls. Add a focused test that a `RuntimeError` from the verification backend still propagates, and verify that invalid argument types are not silently swallowed.
4. **Verify the login caller.** In the new `tests/unit/test_auth.py`, mount the existing auth router on a small FastAPI test app. Override `get_db` with a fake database result containing a synthetic user and malformed hash, without mocking `verify_password()`. Submit form credentials and assert HTTP 401 with `Invalid email or password`, the bearer challenge, and no access token. Include a valid-hash login control. Database fixtures must be local mocks, so these tests need no Docker or real accounts.
5. **Validate and review the focused change.** Run the affected tests, `make check`, and `make test-unit`; then run frontend tests and the integration test command corresponding to the five required CI jobs. Review the complete diff for accidental changes and unrelated markers or suppressions. Record actual commands and outcomes in the Unit 9 journal and PR, then confirm all five CI jobs on the PR.

Commands used for local validation:

```bash
.venv/bin/pytest tests/unit/test_security.py tests/unit/test_auth.py -q --tb=short
make check
make test-unit
make test-integration
cd frontend && npm test -- --run
```

The integration directory currently has no tests. `make test-integration` collected zero tests: pytest exited 5 and Make exited 2. The CI workflow explicitly treats pytest's empty-suite exit as success. This is an observed absence of integration coverage, rather than a passing integration test suite.

## 4. Inputs & outputs

**Helper input:** `plain_password: str` and `hashed_password: str`, with the stored hash supplied from `User.hashed_password`.

**Helper result:** `True` only for a matching valid bcrypt hash; `False` for an incorrect password or a stored hash that Passlib rejects with `ValueError`, including `UnknownHashError`.

**Error boundary:** `TypeError` for unsupported argument types and `RuntimeError` for backend failures continue to propagate. `hash_password()`, token creation, database contents, and the public function signature do not require changes.

**Caller result:** A user whose stored hash is malformed receives the existing HTTP 401 invalid-credentials response. A matching valid hash still allows normal token creation. Route behavior will be verified with the real helper and synthetic database results.

**Reproduction input and output:** `verify_password("password", "not_a_valid_bcrypt_hash")` raised `UnknownHashError` before the fix and now returns exactly `False`.

## 5. Risks & unknowns

- **Exception scope in `core/security.py`:** Catching `ValueError` also catches Passlib's invalid-password-value subclasses. Treat those as failed verification rather than success, and add an oversized-password rejection case to make that choice explicit. Keep the `try` block limited to verification and test that backend `RuntimeError` and argument `TypeError` still escape.
- **Recognized but corrupt bcrypt strings:** Checking only `pwd_context.identify()` or catching only `UnknownHashError` would miss the observed short-salt `ValueError`. Include `$2b$12$invalid` in the regression cases.
- **Password behavior:** Preserve the existing 1,000-character password control and exact whitespace matching in `tests/unit/test_security.py`. Avoid changing truncation settings or normalizing submitted passwords as part of this fix.
- **Seeded test markers:** `test_verify_with_wrong_hash_format` will become a strict XPASS if its marker is left in place after the fix. Remove only the marker for issue #72 / H-05. No matching mypy suppression for `core.security` was found in `pyproject.toml`.
- **Caller-test isolation:** A mock of the verifier would hide the reported defect. Override only the database boundary in `tests/unit/test_auth.py` and exercise the real verifier through the auth router.
- **Dependency differences:** The local environment uses Python 3.13.7 and Passlib 1.9.5, while CI uses Python 3.11 and dependencies specified with lower bounds. The linked stable Passlib reference is version 1.7.4. Assert observable return values and exception classes instead of exact library error text, and verify the PR's actual CI results.
- **Validation side effects:** `make check` includes Black, which writes formatting changes. Inspect its diff and keep the contribution focused on the issue. Preserve unrelated seeded defects and their suppressions.

All helper and caller regression cases pass locally, and all five CI jobs passed before the PR was marked ready for review. There are no current blockers. The [PR checks](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/113/checks) provide the current CI results.

## 6. Edge cases

- **Unrecognized string:** `not_a_valid_bcrypt_hash` returns `False`.
- **Empty stored hash:** `""` returns `False`.
- **Unsupported hash-like string:** `5f4dcc3b5aa765d61d8327deb882cf99` returns `False` under the bcrypt-only context.
- **Truncated bcrypt value:** `$2b$12$invalid` returns `False`, even though the scheme prefix is recognizable.
- **Matching valid bcrypt hash:** A hash produced by `hash_password("correct_password")` verifies successfully for that exact password.
- **Incorrect password with a valid hash:** The same stored hash returns `False` for `wrong_password`.
- **Long and whitespace-containing passwords:** Preserve the established behavior in the existing controls, including the 1,000-character input and significant leading/trailing spaces. A password beyond Passlib's maximum verification size is rejected with `False` under the planned `ValueError` boundary.
- **Unexpected backend failure:** A verification backend raising `RuntimeError` still raises that error, so an operational failure is visible.
- **Invalid argument type:** Passing an unsupported type instead of a password/hash string still raises `TypeError`; this change does not expand the typed API.
