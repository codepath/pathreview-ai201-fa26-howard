## Solution plan

**Issue:** [API reference doc is missing the POST /profiles request body schema #37](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/37)

### Understand

The API reference lists `POST /profiles` and `POST /reviews`, but neither entry explains the request body. The gap is in the written documentation: the backend already defines the fields, but `docs/API.md` does not describe them or provide examples. Readers currently have to inspect the Python files to construct a request.

After the fix, a reader should be able to identify the correct content type, field names, types, required status, and example values from the API reference. Profile creation should be documented as multipart form data, and review creation should be documented as JSON.

### Map

The implementation change will be in `docs/API.md`, under the Profiles and Reviews sections.

I will use these files as references:

- `api/routes/profiles.py`: `create_profile_endpoint` defines the optional form fields `github_username` and `portfolio_url`, the optional upload `resume_file`, and the accepted upload MIME types.
- `api/schemas/profile.py`: `ProfileCreate` defines the optional string fields and their length limits.
- `api/schemas/review.py`: `ReviewCreate` requires `profile_id` as a UUID.
- `api/routes/reviews.py`: `create_review_endpoint` accepts `ReviewCreate` and uses its profile ID to create a review.

`JOURNAL.md` records the reproduction and planning progress. `PLAN.md` will be updated if the investigation changes the approach. No backend behavior changes are planned for issue #37.

### Plan

1. Compare the current Profiles and Reviews documentation with the route signatures and request schemas. Record the fields, defaults, validation limits, and content types so the documentation matches the implementation.
2. Add a multipart request body section for `POST /profiles` in `docs/API.md`. Include a table with each field's type, required status, description, and example value. Explain the optional resume upload and provide a curl example using `-F` so curl generates the multipart boundary.
3. Add a JSON request body section for `POST /reviews`. Describe the required UUID `profile_id`, provide an example value, and include a JSON request example. Explain that callers should use the ID of an existing profile they own.
4. Review every documented field against the Python definitions. Parse the JSON example to check its syntax, validate the example UUID, and check that the multipart example uses the exact field names. Use a Markdown resume in the main upload example to keep verification separate from PDF parsing.
5. Review the rendered Markdown and final diff for readability and scope. Follow the repository's required checks before the implementation PR, and record any failures separately from the documentation change.

### Inputs & outputs

The inputs are the current route definitions and Pydantic request schemas. Profile creation accepts optional `github_username` and `portfolio_url` strings and an optional `resume_file` upload. Review creation accepts a JSON object containing a required `profile_id` UUID.

The output is an updated `docs/API.md` with request body documentation for both endpoints. Each field will have a description and an example value, along with its type and required status. The examples will distinguish multipart form data from JSON and show where callers must supply their own authentication token, resume file, and existing profile ID. Runtime behavior will remain the same.

### Risks & unknowns

- The profile route's docstring mentions PDF and Markdown, but its MIME allowlist also includes `text/plain`. I will base the upload documentation on the actual checks in `api/routes/profiles.py` and explicitly describe the accepted MIME types.
- `ProfileCreate` defines length limits, but the route constructs that model inside its exception handler. I will check this path before describing validation errors and avoid promising an HTTP status that the route does not reliably return.
- A syntactically valid example UUID does not guarantee that a profile exists or belongs to the caller. I will make that distinction clear in the review example and use an actual returned profile ID for any later live verification.
- The PDF branch in `api/routes/profiles.py` passes uploaded bytes to `PyPDF2.PdfReader`. I have not verified that path at runtime. PDF parsing behavior is outside this documentation issue; if it blocks a later example check, I will record it separately rather than expand the fix.
- Static comparison confirms the documentation gap, but it does not establish that example requests succeed against a running service. Any live verification will require authentication and an existing profile. I will distinguish static checks from live results in the Unit 9 notes.

### Edge cases

- A profile request can omit the GitHub username, portfolio URL, or resume upload. The documentation must mark all three as optional and avoid implying that a resume is required.
- A resume upload is a file part, not a JSON string or a server-side file path. The curl example must use `resume_file=@...` and let curl set the multipart boundary.
- The upload allowlist includes `application/pdf`, `text/markdown`, and `text/plain`. The guide must not imply that arbitrary file types are accepted.
- GitHub usernames and portfolio URLs have maximum lengths of 255 and 500 characters respectively in `ProfileCreate`. Example values must stay within those limits.
- Review requests must include a valid UUID for `profile_id`. Missing IDs, malformed UUIDs, nonexistent profiles, and profiles owned by another user must not be presented as valid successful examples.
- Both routes depend on the current authenticated user. Example commands must show how to supply a token without including real credentials.


### Unit 9 progress

Steps 1 through 3 are implemented in `docs/API.md`. Step 4 is covered by two tests in `tests/unit/test_api_documentation.py`: they parse the documented JSON and curl examples, validate the body values against the request schemas, and check authentication and multipart upload syntax. Both tests failed against the original missing examples and passed with the documentation added. The examples have not been sent to a live API.

Local quality checks, unit tests, and frontend tests pass. The integration directory has no tests; its local command exits with code 5, which the current CI workflow accepts. Source review confirmed the upload MIME allowlist and profile length limits. The guide describes those limits without promising a validation status for overlong profile strings. It recommends using an existing owned profile without claiming that review creation enforces ownership. PDF parsing was not changed or tested.

