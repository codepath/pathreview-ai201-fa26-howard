## Unit 7 — Issue selection

**Issue link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47)

**Issue title:** API docs don't include example curl commands 

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The project's API documentation is missing example curl commands that developers can use to interact with the API endpoints. Without these examples, contributors may have difficulty understanding how to format requests, include the necessary information, and test endpoints from the command line. This affects the API documentation and makes it less accessible to developers who are setting up or testing the project. A successful fix would add clear, usable curl examples that demonstrate how to make API requests and help developers test the endpoints more easily.

**Branch name:** docs/47-api-curl-examples

**Setup confirmation:** [Yes] App runs locally at localhost:5173

**Cohort ledger:** [Yes] Issue added to cohort ledger

------------------------------------------------------------------------------------------

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** (https://github.com/palston20/pathreview-ai201-fa26-howard/commit/0e8bcc155682abf2f50ef703416fbb33f62972af)

**Reproduction summary:**
Since this was a documentation issue, I wanted to prove that there were no curl commands listed within the documentation. Using the linux command "grep -in "curl" I was able to check in both the README.md file and also within the docs folder to confirm. 

**PLAN.md link:** (https://github.com/palston20/pathreview-ai201-fa26-howard/commit/2ff6e70972124889335549e2c4c81113e36d6175)


**Blockers or open questions:**
I still need to identify and review the API endpoints, including their HTTP methods, required parameters, authentication headers, and request bodies. I plan to use the FastAPI documentation and the existing API code to make sure the curl examples I create are accurate and functional.


------------------------------------------------------------------------------------------

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Completed the issue reproduction and created PLAN.md outlining the implementation steps. Reviewed the API routes, schemas, and authentication middleware to identify the required HTTP methods, endpoints, request formats, and authentication requirements. Mapped out the curl examples needed for the API documentation.

**Next steps:**
Update docs/API.md with curl examples for the API endpoints, including authentication, profiles, reviews, and health checks. Test the examples against the running API, review the documentation for accuracy,and complete the remaning checks before submitting the pull request 

**Blockers:**
No major blockers. 

---

### Check-in 2 (end of week)

**PR link:** [link to your submitted pull request]

**Branch:** [the branch name you worked on, e.g. `fix/123-short-description`]

**What you built:**
[1–3 sentences summarizing what your fix does and how it works]

**Tests added or updated:**
[Which test files did you touch? What do they cover?]

**Self-review confirmation:** [ ] make check passes  [ ] make test-unit passes

**Draft PR feedback received from:** [name or Slack handle, or "none"]