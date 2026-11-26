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


-----------------------------------------------------------------------------------------------------------

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

**PR link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/pull/115)

**Branch:** docs/47-api-curl-examples 

**What you built:**
Updated the API.md file to include curl examples for the PathReview API endpoints. Added examples for authentication, profile management, reviews, and health checks, including the required headers, request bodies, and JWT bearer token authentication instructions. 

**Tests added or updated:**
No test files added or modified. Manually tested representative API endpoints using Swagger UI, including login, listing reviews, health checks, and profile creation. Verfiied successful authentication and profile/review requests. These health endpoints returned 503 because some dependecies were reported as unhealthy. Ran make test-unit: 375 passed, 53 xfailed, with 4 existing warnings. 

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes
- Note: make check did not complete successfully as a combined command in my local environment. However, I ran its individual components separately: Ruff passed, Black completed formatting, and MyPy reported no issues in 76 source files. The unit test suite also passed with 375 passed and 53 expected failures. No application code was changed for this documentation-only issue.

**Draft PR feedback received from:** None 

-----------------------------------------------------------------------------------------------------------

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No review has come in yet. 

**How you responded:**
N/A

---

### Reflection

**What was harder than you expected?**
Even though my issue was documentation-related, I had to go through multiple route files, schemas, and authentication requirements to make sure my cURL examples were accurate, which was something I did not expect. I also underestimated how much time troubleshooting the development environment and running the required checks would take.

**What did you learn about working in a large codebase?**
Working in someone else's codebase requires a lot more preparation and attention to detail than building something from scratch. I couldn't just make changes based on what I thought would work. I had to understand the existing structure, follow the project's  guidelines, and make sure my work fit the conventions already established by the team.

**How did AI tools help — and where did they fall short?**
AI tools were especially helpful when navigating unfamiliar files, understanding API routes, troubleshooting errors, and breaking larger tasks into smaller steps. 

However, I still needed to inspect the actual code, test API requests, and review the results myself because AI could sometimes make assumptions about the codebase or suggest steps that didn't match my environment.


**What would you do differently if you started over?**
If I started over, I would probably choose an issue that involved making actual changes to the codebase rather than focusing on documentation so that I could gain more hands-on coding experience. However, I do believe the issue I chose was a good starting point for someone who had never contributed to an open-source project before. It allowed me to become more comfortable navigating an unfamiliar repository, understanding the contribution workflow, and learning how to submit a pull request before taking on a more complex coding issue.

**What are you most proud of from this module?**
I'm most proud of being able to contribute to an existing project that I didn't originally build. At first, navigating the repository, understanding the backend, and working with GitHub workflows felt overwhelming. However, I was able to investigate an issue, create a plan, make a meaningful documentation contribution, test my examples, and submit a pull request. I'm proud that I pushed through the unfamiliar parts instead of giving up.