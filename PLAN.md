# Solution plan

**Issue** [#63 — README scorer test fixture is too short for its own word-count assertion](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/63)

## Understand

`test_readme_with_all_quality_signals` passes a sample README with 51 whitespace-separated tokens to the scorer. The scorer returns `success=True` and classifies it as `minimal`, which is correct for fewer than 100 tokens. With pytest's `--runxfail` option, the test fails at `assert 51 > 100` before reaching its `comprehensive` assertion. The test needs a fixture with at least 500 tokens and examples of each quality signal it checks.

## Map

- **Edit** `tests/unit/test_readme_scorer.py`. Update the Markdown string and word-count assertion in `TestReadmeScorer.test_readme_with_all_quality_signals`, then remove the strict expected-failure marker for issue #63.
- **Reference** `agent/tools/readme_scorer.py`. `ReadmeScorer.execute` accepts the fixture and returns a `ToolResult`. `ReadmeScorer._score_readme` defines the token count, category boundaries, quality-signal checks, and aggregate score.

## Plan

1. Expand the fixture into a realistic project README with at least 525 whitespace-separated tokens for a small editing margin. Include a substantive project overview, installation steps, usage examples, features, troubleshooting, and a tech stack. Keep the badge syntax and demo link.
2. Update the count assertion to `data["word_count"] >= 500` and retain the `comprehensive` category and existing quality-signal and score assertions.
3. Run the targeted test with `--runxfail` and confirm that every assertion passes. Remove the issue #63 marker, then rerun the targeted test without flags that alter expected-failure handling.
4. Run `python -m pytest tests/unit/test_readme_scorer.py -q` and review the diff to confirm the change is limited to the targeted test.

## Inputs & outputs

The input is `{"readme_content": readme}`, where `readme` is the Markdown fixture. The test expects `ToolResult.success=True` and data with `has_readme=True`, `word_count >= 500`, `word_count_category="comprehensive"`, all five quality-signal flags true, and `overall_score > 0.7`. The test should pass in a standard pytest run.

## Risks & unknowns

- The count in `ReadmeScorer._score_readme` comes from `len(content.split())`. Markdown markers and code can affect the count, so check `result.data["word_count"]` on the real fixture before removing the marker.
- Removing recognizable headings, the badge syntax, or the demo indicator during the rewrite could turn a signal false in `_score_readme`. Verify the individual assertions in `test_readme_with_all_quality_signals` even when the aggregate score is high.
- A passing test with `pytest.mark.xfail(strict=True)` still reports an unexpected pass as a failure. Verify the test again after removing the marker from `tests/unit/test_readme_scorer.py`.

## Edge cases

| Input or state | Expected scorer behavior |
| --- | --- |
| README with exactly 499 whitespace-separated tokens | Category is `adequate`, even with all five quality signals. |
| README with exactly 500 whitespace-separated tokens | Category is `comprehensive`. |
| README with 525 tokens and no Markdown image syntax | Category is `comprehensive` and `has_badges` is false. The all-signals test should reject that fixture. |
| Empty or whitespace-only README | `has_readme` is false and `word_count` is zero. |
