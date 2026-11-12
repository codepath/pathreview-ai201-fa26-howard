## Solution plan

**Issue:** `verify_password` raises `UnknownHashError` on malformed stored hashes instead of returning False (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/72)

### Understand

`verify_password` in `core/security.py` just returns `bool(pwd_context.verify(plain_password, hashed_password))` with no error handling. When the stored hash isn't something passlib recognizes, `pwd_context.verify` raises `passlib.exc.UnknownHashError` instead of returning a result. When the hash looks like bcrypt but is broken (like a truncated one), the bcrypt handler raises a plain `ValueError`. `UnknownHashError` is a subclass of `ValueError`, so both are `ValueError`s.

- **Expected:** a malformed or unrecognized stored hash means the password can't match, so `verify_password` returns `False`.
- **Actual:** the exception leaks out of `verify_password`.

**Impact on login:** `login()` in `api/routes/auth.py` calls `verify_password` on line 80. The exception isn't an `HTTPException`, so it falls into the generic `except Exception` block. That logs `login_error` with `str(exc)` and returns a 500 "Login failed". A user with a corrupted hash in the database gets a server error instead of a normal 401 "Invalid email or password". So a data problem shows up as a server crash, and the response is different from a normal bad login.

### Map

- `core/security.py`, `verify_password(plain_password, hashed_password)`: the only function I need to change. It uses the module level `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`.
- `tests/unit/test_security.py`, `TestSecurity.test_verify_with_wrong_hash_format`: has `@pytest.mark.xfail(strict=True, reason="issue #72 (manifest H-05): ...")`. Because it's strict, the test will XPASS and fail CI once the fix works, so the marker has to be removed in the same change. This is also where I'll add tests for the other malformed inputs.
- `api/routes/auth.py`, `login()`: read-only caller. I don't need to change it. Once `verify_password` returns `False`, the existing `if not user or not verify_password(...)` branch already returns a 401.

### Plan

1. In `verify_password`, wrap `pwd_context.verify(...)` in `try/except ValueError` and return `False` in the except block. Catching `ValueError` covers `UnknownHashError` (a subclass) and the plain `ValueError` from truncated bcrypt hashes.
2. Update the docstring so it says malformed or unrecognized hashes return `False` instead of raising.
3. Remove the strict `xfail` marker from `test_verify_with_wrong_hash_format`.
4. Add tests (probably one parametrized test) for `""`, `"$2b$12$short"` and `"$argon2id$v=19$xx"` that assert `verify_password` returns `False`. Also check that a valid hash with the right password still returns `True`.
5. Run `make check && make test-unit` and make sure everything passes with no XPASS.

### Inputs & outputs

| Input (`hashed_password`) | Today | After the fix |
|---|---|---|
| Valid bcrypt hash, correct password | `True` | `True` |
| Valid bcrypt hash, wrong password | `False` | `False` |
| `"not_a_valid_bcrypt_hash"` | raises `UnknownHashError` | `False` |
| `""` | raises `UnknownHashError` | `False` |
| `"$2b$12$short"` | raises `ValueError` | `False` |
| `"$argon2id$v=19$xx"` | raises `UnknownHashError` | `False` |

Login endpoint with a malformed stored hash: today 500 "Login failed", after the fix 401 "Invalid email or password".

### Risks & unknowns

- **Catching too broadly:** I don't want `except Exception`, because that could hide real bugs like a missing bcrypt backend. `ValueError` is narrower, but it could still hide some unrelated `ValueError` from inside passlib. Catching only `UnknownHashError` would be the tightest option, but my testing shows it misses the truncated bcrypt case. Right now I'm leaning toward `ValueError`.
- **Logging:** a malformed hash in the database is a data problem someone should probably know about. If I log a warning, it must not include the hash or the password. The codebase uses structlog (`log = structlog.get_logger()` in `api/routes/auth.py` and `core/services/*`), so I'd follow that. `core/security.py` doesn't have a logger yet, so I need to decide whether adding one is in scope.
- **Existing tests:** the other 24 tests in `test_security.py` (hash and verify round trips, long passwords, tokens) have to keep passing.
- **bcrypt version warning:** passlib 1.7.4 prints "(trapped) error reading bcrypt version" with bcrypt 4.3.0. It's harmless and not part of this issue, but I shouldn't confuse it with my change.

### Edge cases

Tested with passlib 1.7.4 and bcrypt 4.3.0:

- `"not_a_valid_bcrypt_hash"` raises `passlib.exc.UnknownHashError: hash could not be identified`
- `""` (empty string) raises `passlib.exc.UnknownHashError: hash could not be identified`
- `"$2b$12$short"` (truncated bcrypt) raises `ValueError: salt too small (bcrypt requires exactly 22 chars)`. This is not an `UnknownHashError`.
- `"$argon2id$v=19$xx"` (argon2 style, not in our `schemes`) raises `passlib.exc.UnknownHashError: hash could not be identified`
- A valid hash from `hash_password("password")` with the correct password returns `True`, and with a wrong password returns `False`. Both have to stay that way.
