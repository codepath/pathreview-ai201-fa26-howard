## Unit 7 — Issue selection

**Issue link:** [(https://github.com/codepath/pathreview-ai201-fa26-howard/issues/11)]

**Issue title:** [Architecture doc doesn't explain the hybrid retrieval scoring formula]

**Tier:** [X] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The architecture guide says PathReview combines vector search and keyword search, but it doesn’t explain how those results are scored together. In rag/retriever/hybrid.py, each set of scores is normalized and then blended using default weights of 70% vector and 30% keyword. I’ll update docs/ARCHITECTURE.md with the formula and a simple example so contributors can understand how the final ranking is calculated.

**Branch name:** docs/11-hybrid-scoring-formula

**Setup confirmation:** The app successfully runs locally at localhost:5173

**Cohort ledger:** [/] Issue added to cohort ledger

**Selection Reasoning**

I chose this issue because this course is my introduction to contributing to a larger codebase, and this Tier 1, good-first-issue task feels like a manageable place to practice. I read the relevant retrieval code and understand that the work is to document the existing scoring formula, default weights, and an example in `docs/ARCHITECTURE.md`, It is done when contributors can follow how the two scores are normalized and blended. The issue estimates 2–3 hours, has no stated blockers, and the change is documentation-only, so I do not expect to need code or test changes. I reviewed the issue comments and claimed it. I still need to check the cohort ledger's Claims count.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/OluchiEmenike/pathreview-ai201-fa26-howard/commit/717553fd498a3237d23ded788fe22e325f3e13ab

**Reproduction summary:**
I compared the hybrid retrieval description in `docs/ARCHITECTURE.md` with `HybridRetriever` in `rag/retriever/hybrid.py`. The guide mentions vector and keyword search but omits the score normalization, default weights, and blending formula that the code uses.

**PLAN.md link:** [PLAN.md](./PLAN.md)

**Blockers or open questions:**
- Should the explanation cover only how normalized vector and keyword scores are blended, or also explain how each search method produces its original score?
- Should the example include a result found by only one search method, where the missing score contributes zero?

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Added a hybrid retrieval scoring subsection to `docs/ARCHITECTURE.md`. It explains separate max-score normalization, the default 0.7/0.3 weighted sum, a worked example, and how a missing score is handled. Validation passed: Ruff, Black formatting check, and mypy all passed; unit tests reported 375 passed and 53 expected failures. `git diff --check` also passed.

**Next steps:**
Commit and push the changes, then open a draft PR and request peer or mentor feedback before submitting it. The `make` command is unavailable in my current PowerShell, so I ran the equivalent project tools from `.venv\Scripts` directly.

**Blockers:**
I am working after the scheduled feedback window, so I need to ask the instructor whether late peer or mentor feedback is still available.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/112

**Branch:** `docs/11-hybrid-scoring-formula`

**What you built:**
I updated `docs/ARCHITECTURE.md` with an explanation of the hybrid retrieval scoring behavior. The documentation now describes separate vector and BM25 result normalization, the default 0.7 vector / 0.3 keyword weights, the blended-score formula, a worked example, and missing-score handling.

**Tests added or updated:**
Not applicable; this is a documentation-only change. Ruff, Black's formatting check, mypy, `git diff --check`, and the unit test suite were run locally.

**Self-review confirmation:** [x] Equivalent project checks pass locally (`ruff`, `black --check`, `mypy`)  [x] Unit tests pass locally (`375 passed, 53 xfailed`)

**Draft PR feedback received from:** 
I did not receive feedback because I did not request a review early.

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — no review received yet

**Summary of feedback:**
No reviewer feedback has come in yet.

**How you responded:**
No feedback to respond to.
---

### Reflection

**What was harder than you expected?**
Getting through the contribution workflow on Windows took more troubleshooting than I expected. The project instructions use `make`, which was unavailable in my PowerShell, and pushing also required resolving GitHub authentication. I had to find equivalent local checks and verify the branch and PR state rather than assume each step had completed. I also downloaded the wrong docker so set up was a hassle in general for me. 

**What did you learn about working in a large codebase?**
I learned to trace a documentation claim back to the implementation before describing it. Reading `HybridRetriever` helped me document the normalization, default weights, and missing-score behavior more accurately. This project helped me understand code documentation in general. I think previously I had tried to be detailed in my understanding but this really demanded my full understanding.

**How did AI tools help — and where did they fall short?**
AI tools helped me locate the relevant retrieval code, understand the scoring flow, organize a solution plan, and run focused validation. I still needed to check the code and command results myself. Generic setup instructions did not always match my Windows shell, and GitHub authentication could not be completed automatically.

**What would you do differently if you started over?**
I would verify my GitHub authentication and local development commands earlier, request a peer review as soon as I had a draft PR, and start the work earlier so there was more time to incorporate feedback before the deadline.

**What are you most proud of from this module?**
I followed the issue from selection through investigation, planning, documentation, local checks, and a submitted PR. I’m proud that I stayed focused on the requested documentation gap and actually applied my knowledge from earlier projects into this one. 