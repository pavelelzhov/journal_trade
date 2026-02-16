# Project rules (MUST)

## Non-negotiables
- Deterministic only. No LLM usage for parsing.
- If uncertain -> return DRAFT, never guess.
- Golden tests are the source of truth. Never auto-regenerate golden files during tests.
- Changes only via Pull Request (no direct commits to main).
- Every PR must pass: pytest + python -m py_compile (or equivalent CI step).

## Parsing rules
- Input may contain Cyrillic, typos, weird punctuation.
- Default position size: 1% if not specified.
- Preserve raw_text; normalized_text is allowed.
