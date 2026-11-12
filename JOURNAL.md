## Unit 7 — Issue selection 

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/60
**Issue title:** Faithfulness checker crashes when a context chunk has `text: None`
**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3 

**Problem summary:** 
The `FaithfulnessChecker` crashes with a `TypeError` when a context chunk's text is explicitly set to `None`. This happens because `.get("text", "")` returns `None` instead of the default empty string when the key exists but has a null value, causing the subsequent string join operation to fail. A successful fix will ensure the method handles `None` values correctly without crashing the application.

**Branch name:** fix/60-faithfulness-checker-crash

**Setup confirmation:** 
[x] App runs locally at localhost:5173 

**Cohort ledger:** 
[x] Issue added to cohort ledger