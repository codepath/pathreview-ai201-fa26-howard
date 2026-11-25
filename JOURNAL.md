## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/37

**Issue title:** API reference doc is missing the POST /profiles request body schema

**Tier:** Tier 1

**Problem summary:**
The API reference in `docs/API.md` lists the profile and review endpoints, but it does not explain what data to send when creating either one. Someone using the API has to read the Python code to figure out the fields and how to format their requests. For `POST /profiles`, the documentation needs to explain the multipart form fields, including the optional resume upload, rather than show a JSON body. For `POST /reviews`, it needs to describe the JSON body containing a profile ID. A successful fix would give each field a description and an example value that matches the existing implementation.

**Branch name:** `docs/37-api-request-body-schemas`

**Setup confirmation:** The app runs locally at localhost:5173.

**Cohort ledger:** I added issue #37 to the cohort ledger.

**Selection notes and scope reasoning:**
I chose this issue because the expected result is clear and the change is limited to the API documentation. I found and reviewed the profile creation route and the review request schema. The profile route accepts multipart form fields and an optional resume upload, while the review schema requires a profile ID in JSON. This gives me a concrete reference for writing accurate field descriptions and examples.

The issue is labeled Tier 1, good first issue, enhancement, api, and docs. That fits the scope because I expect to edit only `docs/API.md`. My plan is to document each field's type, whether it is required, and an example value, then compare the examples with the existing code. I also read a related review service test to understand how review creation is tested. That test does not check request examples, so I still need to determine the appropriate validation for this documentation change.

The issue estimates 2 to 3 hours, and I have budgeted 3 to 4 hours to include verification and PR preparation. This fits my schedule before the Unit 9 deadline. I commented on the issue to claim it and checked the issue comments and ledger for other claims. I am comfortable proceeding with the number of people working on it. I also checked for blockers and dependencies and found none that would prevent me from starting.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/abeeralrijal/pathreview-ai201-fa26-howard/commit/5badb7d8f07ab0bc2f92a0877704725027c861ac

**Reproduction summary:**
I reproduced the documentation gap by opening the Profiles and Reviews sections in my local `docs/API.md` and comparing them with `create_profile_endpoint` and `ReviewCreate`. The guide lists both POST endpoints but omits their request fields, content types, and example values, even though the backend already defines them.

**Local reproduction steps and observations:**

1. Open `docs/API.md` and read the Profiles and Reviews sections. Both POST entries contain only a short description, with no request body table or example.
2. Open `api/routes/profiles.py` and read `create_profile_endpoint`. It accepts `github_username` and `portfolio_url` as form fields and `resume_file` as a file upload, all with defaults of `None`.
3. Read `ProfileCreate` in `api/schemas/profile.py` to confirm the optional string fields and their length limits.
4. Open `api/schemas/review.py` and read `ReviewCreate`. It requires `profile_id` as a UUID. Then read `create_review_endpoint` in `api/routes/reviews.py` to confirm that it accepts that request model.
5. Compare these definitions with the API reference. The multipart profile fields and JSON review field are absent from the written guide, which confirms issue #37 locally.

This reproduction is a comparison of the local documentation and source code. It does not depend on triggering an API error or making a live request.

**PLAN.md link:** [Solution plan](https://github.com/abeeralrijal/pathreview-ai201-fa26-howard/blob/docs/37-api-request-body-schemas/PLAN.md)

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:**
There are no blockers to writing the documentation. The upload code accepts plain text as well as PDF and Markdown, so the guide needs to reflect the actual MIME allowlist. I will verify the examples against the route and schema definitions and avoid claiming that live requests have been tested until I run them. The plan records the validation and PDF parsing details that need care during implementation.


## Unit 9: Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
The request documentation for both endpoints is implemented in `docs/API.md`. It includes field tables, content types, authentication instructions, and curl examples. The source comparison and documentation tasks in steps 1 through 3 of `PLAN.md` are complete. Two regression tests were added to validate the examples against the request schemas; both failed before the documentation was added and passed afterward.

**Next steps:**
Review the local diff, commit and push the changes, and open a draft PR using the repository template. Request feedback from a classmate or mentor in the cohort's Slack channel. Address the feedback, check all five CI jobs, and add the submitted PR link below before the deadline.

**Blockers:**
No implementation blockers remain. The remaining steps at this stage were PR submission, peer feedback, and CI verification.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/107

**Branch:** `docs/37-api-request-body-schemas`

**What you built:**
The API reference now explains the multipart request for `POST /profiles` and the JSON request for `POST /reviews`. Each request field has a type, required status, description, and example value. The guide also includes authenticated curl examples and explains optional uploads and valid profile IDs.

**Tests added or updated:**
Added `tests/unit/test_api_documentation.py` with two unit tests that read the examples directly from `docs/API.md`. They validate the review JSON against `ReviewCreate`, check that the review curl body matches that JSON, and validate the profile curl field names, file upload syntax, authentication header, and text values against `ProfileCreate`. The tests cover example construction, not live API requests or successful review processing. No xfail marker or baseline suppression was tied to issue #37, so none was removed.

**Self-review confirmation:**

- [x] `make check` passes.
- [x] `make test-unit` passes.

`make check` passes, including Ruff, Black, and mypy. `make test-unit` passes with 377 tests passed and 53 expected failures. The first unit run could not download tiktoken's encoding data in the restricted environment; the rerun with network access passed. The frontend tests also pass with 18 tests passed. `make test-integration` collects no tests and exits with code 5; the existing CI workflow explicitly treats this empty suite as success. The PR is open and ready for review. All five GitHub CI jobs passed: lint, typecheck, test-unit, test-integration, and frontend.

**Draft PR feedback received from:** None. I requested feedback, but did not receive a response before submitting. Because I submitted late, I did not leave enough time for peer feedback.

The PR is ready for review with all five CI checks passing. Peer feedback was not received, so I have not claimed that a peer reviewed the work.

## Unit 10 — Iteration & reflection

### Review record

**Did you receive reviewer feedback?**

- [ ] Yes
- [x] No

As of November 25, I had received no reviewer comments, so there were no review responses or follow-up changes to document. [Pull request #107](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/107)

### Reflection

#### 1. What was harder than you expected?

I chose issue #37 because documenting two existing endpoints looked like a manageable first contribution, but verification took more work than I expected. The first full unit test run failed because the restricted environment blocked the download of tiktoken's encoding data. I reran it with network access and got 377 passes and 53 expected failures. [Issue #37](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/37)

#### 2. What did you learn about working in a large codebase?

I learned to trace a request across the route and the schema before writing about it in `docs/API.md`. The route in `api/routes/profiles.py` defined the multipart fields and upload rules, while `ProfileCreate` defined the text length limits. The route's docstring mentioned PDF and Markdown, but reading the upload check showed that it also accepted plain text.

#### 3. How did AI tools help, and where did they fall short?

Codex helped me revisit my Unit 8 plan and Unit 9 notes so I could see how my approach changed as I worked on issue #37. It could summarize the tests I added, but I had to decide what those results justified saying in the PR: the examples matched the request schemas, and I would still need to run them against the API to verify the full workflow. Using AI to organize my notes saved time, and checking its wording against the code and test results helped me make claims I could explain to a reviewer.

#### 4. What would you do differently if you started over?

I would open PR #107 as a draft earlier because my late submission left little time for peer feedback. I would ask a peer to try the curl examples with a running instance, starting with an authenticated profile request and using the returned ID to start a review. That would show me where the guide leaves readers guessing and give me time to revise it before submission.

#### 5. What are you most proud of from this module?

I'm most proud that I added two tests in `tests/unit/test_api_documentation.py` that read the examples directly from the guide. Both failed against the original guide and passed after I added the examples, so the tests can catch future edits that break the documented request format. I can explain exactly what they verify, including the multipart field names and the review UUID, and what would still need a live test. [Implementation commit](https://github.com/abeeralrijal/pathreview-ai201-fa26-howard/commit/f52f9575e8b5aa0723526924c60b7baa464eefd3)
