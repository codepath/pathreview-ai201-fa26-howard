# PathReview Module 3 Journal

- **Student:** Shreejay Subedi
- **GitHub:** [shreejaysubedi](https://github.com/shreejaysubedi)
- **Fork:** [pathreview-ai201-fa26-howard](https://github.com/shreejaysubedi/pathreview-ai201-fa26-howard)

## Unit 7 — Issue selection and setup

**Work date:** November 25, 2026 (America/New_York)

### Selected issue

- **Issue:** [#72](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/72)
- **Title:** `verify_password` raises `UnknownHashError` on malformed stored hashes instead of returning False
- **Tier:** Tier 1 (`tier-1`, `good first issue`, `bug`, `api`)
- **Branch:** `fix/72-malformed-password-hashes`
- **Working-branch URL:** https://github.com/shreejaysubedi/pathreview-ai201-fa26-howard/tree/fix/72-malformed-password-hashes
- **Claim confirmation:** [Comment posted on issue #72](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/72#issuecomment-7175847862)

### Problem summary

PathReview checks a login password against a stored bcrypt hash using `verify_password()` in `core/security.py`. The function currently passes the stored value directly to Passlib, so an unrecognized hash can raise `UnknownHashError` instead of returning a boolean. The login route catches that error as an unexpected failure and returns a server error rather than rejecting the credentials normally. A successful fix will return `False` for malformed stored hashes while preserving the existing behavior for correct and incorrect passwords against valid bcrypt hashes.

### Issue-fit checklist and selection reasoning

- **Clear target:** The issue names the verification function and its existing regression test. Its expected outcome is a concrete boolean result.
- **Affected implementation:** `core/security.py`, specifically `verify_password()`.
- **Caller to verify:** `api/routes/auth.py`, specifically `login()`, which uses the result to reject invalid credentials.
- **Nearby tests:** `tests/unit/test_security.py` already covers valid passwords, incorrect passwords, case sensitivity, salt behavior, empty passwords, and special characters. `test_verify_with_wrong_hash_format` is marked `xfail(strict=True)` for issue #72 / manifest H-05.
- **Before and after:** A malformed stored hash currently escapes as an exception. After the fix, verification should return `False`, allowing the login route's existing invalid-credentials response.
- **Scope:** One authentication helper and focused tests provide a manageable contribution for catching up. The issue's stated estimate is 1–2 hours for the fix, with setup and course documentation taking additional time.
- **Dependencies:** Passlib and bcrypt are already project dependencies. The relevant unit tests can run without calling an LLM or using a real GitHub token.
- **Risk to investigate in Unit 8:** Identify the specific malformed-hash exceptions that should become `False` without hiding unrelated programming errors. Preserve verification of valid bcrypt hashes.
- **Completion evidence to produce later:** Add or strengthen regression cases, remove only the issue #72 `xfail` marker when the fix passes, and run the required checks.

### Code and data-flow notes

1. `frontend/src/pages/LoginPage.tsx` collects the login credentials.
2. `frontend/src/services/api.ts` sends them to `POST /auth/login` through Vite's `/api` proxy.
3. `api/routes/auth.py::login()` looks up the user and passes the submitted password and stored hash to `core/security.py::verify_password()`.
4. Passlib's bcrypt context performs the comparison. A `False` result leads to HTTP 401; an unexpected exception reaches the login route's HTTP 500 handler.
5. `tests/unit/test_security.py` exercises the helper's public behavior, including the seeded malformed-hash case.

### Setup confirmation

- [x] Forked and cloned the Howard repository.
- [x] Read `README.md`, `docs/SETUP.md`, `docs/CONTRIBUTING.md`, and `docs/ARCHITECTURE.md`.
- [x] Read the issue body, relevant helper, login caller, and nearby tests.
- [x] Added `upstream` pointing to `https://github.com/codepath/pathreview-ai201-fa26-howard.git`.
- [x] Created the working branch named above.
- [x] Created an ignored `.env` from `.env.example`, using `LLM_PROVIDER=mock`.
- [x] Created `.venv`, installed the backend and development dependencies, and installed the repository's pre-commit hook.
- [x] Installed frontend dependencies using `npm ci`.
- [x] Started PostgreSQL, Redis, and ChromaDB; all three passed their container health checks.
- [x] Ran database migrations to revision `002 (head)` and seeded the supplied demo accounts and reviews.
- [x] Started the application with `make run` and opened `http://localhost:5173`.
- [x] Logged in with the supplied `user1@example.com` demo account and verified the dashboard displayed its three seeded reviews.

![Verified local dashboard after demo login](docs/evidence/unit7-dashboard.jpg)

Local tool versions: Python 3.13.7, Node.js 22.20.0, npm 10.9.3, Docker 29.0.1, and Docker Compose 2.40.3. The repository's CI uses Python 3.11; CI results will be checked with the later PR.

### Setup issues and resolutions

- **Docker Desktop was stopped:** Started it before bringing up the backing services.
- **Occupied ports:** An existing local app uses ports 5433 and 8001. PathReview uses PostgreSQL on 15433 and ChromaDB on 18001 through an ignored local Compose override at `.venv/compose.local.yml`. The ignored `.env` points to those ports.
- **ChromaDB image compatibility:** The pinned `chromadb/chroma:0.4.22` image failed because its startup dependency installation selected NumPy 2, which removed `np.float_`. The local override mounts `.venv/chroma-constraints.txt` containing `numpy<2` and sets `PIP_CONSTRAINT` to that file inside the container.
- **ChromaDB health check:** The image lacks `curl`, so the local override checks the same heartbeat endpoint using Python's `urllib.request`.
- **Tokenizer download:** The first unit-test run could not download `cl100k_base` inside the restricted network environment. Downloaded its tokenizer data with network access, then reran the suite successfully.

To start backing services again on this machine:

```bash
docker compose -f docker-compose.yml -f .venv/compose.local.yml up -d --wait
make run
```

The port and dependency workarounds are local setup files inside ignored `.env` / `.venv` paths. This journal records them so the local setup can be understood and repeated.

### Baseline checks actually run

- `make test-unit`: **375 passed, 53 xfailed**. The expected failures include seeded course defects.
- `make lint`: **passed**.
- `.venv/bin/python -m pip check`: **passed**.
- `cd frontend && npm test -- --run`: **18 passed** across two test files.
- `cd frontend && npm run build`: **passed**.
- `GET http://localhost:8000/`: returned the running API message.
- ChromaDB's heartbeat endpoint responded, and all three containers passed health checks.

### Cohort ledger and submission status

**Cohort-ledger confirmation: pending.** The Howard ledger row has not been entered or verified. Google Drive access is not connected in this session.

Ledger: https://docs.google.com/spreadsheets/d/1-39i16vRXrVwGKUHwxWfg2w_UAgsmxUYaR1oJ2djH8w

Row values to enter in the **Howard** tab: **Shreejay Subedi**, **shreejaysubedi**, **issue #72**. Leave the PR link blank until a PR exists.

**Unit 7 course submission: pending.** Submit the working-branch URL above in Unit 7's project submission form after confirming the journal is visible on that branch.

### AI assistance

Codex inspected the repository and live issue, helped configure and verify the local environment, posted the approved claim comment, and drafted this journal from the observed results. The initial suggestion to skip an already claimed issue was corrected after the course brief clarified that claims are non-exclusive. Issue #72 was chosen for its focused scope and smaller stated estimate.
