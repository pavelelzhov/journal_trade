# Parsing Spec v1

## Goal
Parse messy trader messages (RU/EN, typos, Cyrillic letters inside tickers) into structured SignalDraft.
NO LLM. Deterministic only.

## Input
Any text (single setup or multiple setups).

## Output
ParseResult:
- status: READY | DRAFT | REJECT
- confidence: 0..1
- signal: SignalDraft (if any)
- errors[], warnings[]

## Default rules
- If position entry allocation is not specified -> default total position percent = 1%.
- If multiple entries and no allocation -> split equally.
- Never guess silently. If uncertain -> DRAFT with warnings/errors.

## Normalization
- Numbers:
  - "67 887,60" -> 67887.60
  - "0,,5" -> 0.5
  - remove thousand spaces, replace comma with dot.
- Tickers homoglyph map (Cyrillic -> Latin) before validation:
  - АВЕСКМНОРТХУ -> A B E C K M H O P T X Y (and lowercase)
- Strip ticker wrappers: $, #, spaces, slashes.

## Splitter
Split long text into blocks by:
- [trader #X] markers
- lines containing $TICKER/#TICKER
- lines like "TICKER LONG/SHORT"

## Extract
Required for READY:
- symbol (normalized and valid)
- side (long/short)
- SL
- entry (market allowed with price=null but then warning)
- at least one TP (can be single TP)

Entries:
- market entry: "Вход рынок" or "entry market" (price may be missing)
- limit entry: "Вход лимитка 67900" or list of prices
- zone entry: "77400-300" interpreted as [77100..77400] with warning

Allocation:
- "82,15 0,3%" near entry line => alloc_pct_abs for that entry
- "(1/3)" => alloc_frac; if total not provided => total=1%

## Validation
- long: SL < entry, TP > entry
- short: SL > entry, TP < entry
If conflicts -> DRAFT (no auto-fix)

## Status
- READY: required fields present and validation passed
- DRAFT: missing fields, ambiguous symbol, zone assumption, logic conflicts
- REJECT: not a signal (no symbol+side and not enough fields)
