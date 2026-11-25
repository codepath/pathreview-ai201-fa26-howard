## Unit 7 — Issue Selection

**Issue link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/75)

**Issue title:** README and .env.example disagree about which LLM API key to set #75

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
This is an issue occurring in the docs specifically. README.md and .env.example have conflicting information about the LLM API to be used. This is an issue because the specific API is important to how to entire codebase is set up and how the code is written. Conflicting information will confuse developers involved. A successful fix will be to have the correct API listed in both documents.

**Branch name:** fix/75-api-disagreement-in-docs

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

## Unit 8 - Issue Reproduction and Fix Planning

**Issue Reproduction:** 
In Line 24 of README.md there is a comment that says to add OPENROUTER_API_KEY to the .env file. This contrasts from line 17 of .env.example which lists the options as "mock" (default, no API key needed) and "openai". These are differing instructions.

**Reproduction commit link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/commit/b5ccd0f0a2e7793188f397db61e3b2a3ca687fce)

**Reproduction summary:**
I went into the docs listed in the issue link, and found exactly where the issue was located.

**PLAN.md link:** (https://github.com/selmaapara224/pathreview-ai201-fa26-howard/blob/fix-75-api-docs/PLAN.md)


**Blockers or open questions:**
I need to ensure that I pick the correct API to list in both docs.


## Unit 9 — Solution building & PR submission

### Check-in 1 

**Current progress:**
I used Claude to understand how the codebase flowed and which API instruction was correct. I have edited README.md, .env.example, as well as SETUP.md which was not orignally anticipated.

**Next steps:**
I will submit the pull request.


---

### Check-in 2 (end of week)

**PR link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/pull/111)

**Branch:** fix/75-api-disagreement-in-docs

**What you built:**
The documents align on API instructions, and provide information onto the specific choices.

**Tests added or updated:**
N/A

**Self-review confirmation:** [X] make check passes  [X] make test-unit passes

**Draft PR feedback received from:** none