# Issue #47 Plan: Add API `curl` Examples

Issue: [#47 — API docs don't include example `curl` commands](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47)

## Problem summary

`docs/API.md` lists the PathReview endpoints but does not show how to invoke
them. A developer setting up the project has no quick, copyable way to verify
that the API is running, authenticate, create a profile, or request a review.

## Reproduction

1. Open `docs/API.md`.
2. Find the endpoint list for health, authentication, profiles, and reviews.
3. Observe that the document describes routes but contains no `curl` commands,
   no bearer-token setup, and no examples that carry IDs between requests.

## Scope

- Add shell-ready `curl` examples to `docs/API.md` for every route registered
  by `api/main.py`.
- Show the required authentication flow and reuse the resulting token in each
  protected request.
- Show how to save profile and review IDs for the dependent examples.
- Include optional resume upload and the documented pagination parameters.

This issue is documentation-only. It does not change route behavior, request
schemas, or response schemas.

## Implementation plan

1. Compare every route in `api/routes/` with the API reference and identify
   omitted routes (`/`, profile update, and review status).
2. Add a small environment-variable setup block, then document each route with
   its method, authentication requirement, and a copyable command.
3. Use the actual request formats from the schemas: JSON for registration,
   form-urlencoded data for login, multipart form data for profile creation,
   and JSON for profile updates and review creation.
4. Review the examples against the route implementations and verify the
   Markdown has no whitespace errors.

## Validation

- `git diff --check`
- `make lint` (when the project virtual environment is available)
- Manual review that each route in `api/main.py` has a matching example and
  that authenticated examples send `Authorization: Bearer $TOKEN`.

## PR summary

Add end-to-end `curl` examples to the API reference, including authentication,
profile lifecycle, review lifecycle, health, and root checks. This gives new
contributors a practical smoke-test sequence after starting the app.
