## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/54 

**Issue title:** Resume section detection fails on text with leading whitespace

**Tier:** [x] Tier 1  

**Problem summary:** The resume parser can't detect any sections when the header lines are indented. In ingestion/parsers/resume_parser.py, _detect_sections() only recognizes a header like "Education" or "Skills" when it's the very first thing on its line. Text extracted from PDFs often keeps its leading spaces, so for those resumes detected_sections comes back empty even though the sections are there. A successful fix would make detection ignore leading whitespace, so indented and non-indented resumes give the same sections and the three related tests in tests/unit/test_resume_parser.py pass.

**Branch name:** bug/54-resume-section-detection

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger