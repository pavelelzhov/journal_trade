from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CYR_TO_LAT = str.maketrans(
    {
        "А": "A", "В": "B", "Е": "E", "С": "C", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "Т": "T", "Х": "X", "У": "Y",
        "а": "a", "в": "b", "е": "e", "с": "c", "к": "k", "м": "m", "н": "h", "о": "o", "р": "p", "т": "t", "х": "x", "у": "y",
    }
)

TRADER_SPLIT_RE = re.compile(r"(?i)\btrader\b")
SYMBOL_SIDE_LINE_RE = re.compile(r"(?i)^\s*[$#]?[A-Za-zА-Яа-я]{2,20}(?:USDT)?\b.*\b(long|short|лонг|шорт)\b")
SIDE_RE = re.compile(r"(?i)\b(long|short|лонг|шорт)\b")
SL_RE = re.compile(r"(?i)\b(sl|stop|стоп|стоп\s*лосс)\b")
TP_RE = re.compile(r"(?i)\b(tp\d*|[tт]ейк|take\s*profit|[tт]ейк\s*профит)\b")
ENTRY_MARKET_RE = re.compile(r"(?i)\b(вход\s*(по\s*)?рынку|entry\s*market|вход\s*с\s*текущих|вход\s*рынок)\b")
ENTRY_LINE_RE = re.compile(r"(?i)\b(вход|entry|усреднение|лимитк)\b")
NUMBER_TOKEN_RE = re.compile(r"-?\d[\d\s]*(?:[.,]\d+)?")
VALID_SYMBOL_RE = re.compile(r"^[A-Z]{2,15}(USDT)?$")


@dataclass
class ParseResult:
    status: str
    confidence: float
    signal: dict[str, Any] | None
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_number(raw: str) -> float | None:
    s = raw.strip().replace("\u00a0", " ")
    if not s:
        return None
    s = s.replace(" ", "").replace(",,", ",").replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    if s.count(".") > 1:
        h, *t = s.split(".")
        s = h + "." + "".join(t)
    if s in {"", ".", "-", "-."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def normalize_symbol(raw: str) -> str:
    return raw.translate(CYR_TO_LAT).replace("$", "").replace("#", "").replace("/", "").replace(" ", "").upper()


def _is_valid_symbol(sym: str | None) -> bool:
    return bool(sym and VALID_SYMBOL_RE.match(sym) and sym not in {"LONG", "SHORT"})


def split_setups(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[list[str]] = []
    cur: list[str] = []

    def flush() -> None:
        nonlocal cur
        if any(x.strip() for x in cur):
            blocks.append(cur)
        cur = []

    for line in lines:
        trigger = bool(TRADER_SPLIT_RE.search(line) or SYMBOL_SIDE_LINE_RE.search(line))
        if trigger and any(x.strip() for x in cur):
            if any("$" in x or "вход" in x.lower() or "tp" in x.lower() or "stop" in x.lower() for x in cur):
                flush()
        cur.append(line)
    flush()
    return ["\n".join(b).strip() for b in blocks if any(x.strip() for x in b)]


def _extract_symbol(block: str) -> str | None:
    candidates: list[str] = []
    for m in re.finditer(r"[$#]\s*([A-Za-zА-Яа-я]{2,20}(?:USDT)?)", block):
        candidates.append(normalize_symbol(m.group(1)))
    for line in block.splitlines():
        m = re.search(r"(?i)^\s*([A-Za-zА-Яа-я]{2,20}(?:USDT)?)\b.*\b(long|short|лонг|шорт)\b", line)
        if m:
            candidates.append(normalize_symbol(m.group(1)))
    for c in candidates:
        if _is_valid_symbol(c):
            return c
    return None


def _extract_side(text_low: str) -> str | None:
    if re.search(r"\b(long|лонг)\b", text_low) or "🐂" in text_low:
        return "long"
    if re.search(r"\b(short|шорт)\b", text_low) or "🐻" in text_low:
        return "short"
    return None


def _first_number(text: str) -> float | None:
    for m in NUMBER_TOKEN_RE.finditer(text):
        v = normalize_number(m.group(0))
        if v is not None:
            return v
    return None


def _parse_entry(block: str, warnings: list[str]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    lines = block.splitlines()
    entries: list[dict[str, Any]] = []
    in_entry = False
    market = ENTRY_MARKET_RE.search(block.lower()) is not None

    for line in lines:
        low = line.lower()
        if SL_RE.search(low) or TP_RE.search(low):
            in_entry = False

        if ENTRY_LINE_RE.search(low):
            in_entry = True

        if not in_entry:
            continue

        # explicit ranges in entry context only
        rm = re.search(r"(\d[\d\s.,]*)\s*-\s*(\d[\d\s.,]*)", line)
        if rm:
            a = normalize_number(rm.group(1))
            b = normalize_number(rm.group(2))
            if a is not None and b is not None:
                lo, hi = (a - b, a) if (a >= 1000 and 1 <= b < 1000) else tuple(sorted((a, b)))
                entries.append({"type": "zone", "price_min": lo, "price_max": hi})
                warnings.append("zone entry interpreted from range")
                continue

        cleaned = re.sub(r"^\s*[-—]?\s*\d+[).]\s*", "", line)
        cleaned = re.sub(r"(?i)^\s*(вход|entry|усреднение)\s*[:;\-]?\s*", "", cleaned)
        n = _first_number(cleaned)
        if n is not None:
            entries.append({"type": "limit", "price": n})

    uniq: list[dict[str, Any]] = []
    seen: set[tuple[tuple[str, Any], ...]] = set()
    for e in entries:
        key = tuple(sorted(e.items()))
        if key not in seen:
            seen.add(key)
            uniq.append(e)

    if market:
        market_price = None
        for line in lines:
            if ENTRY_MARKET_RE.search(line.lower()):
                market_price = _first_number(line)
                break
        if market_price is None:
            warnings.append("market entry without explicit price")
        return {"type": "market", "price": market_price}, uniq
    return (uniq[0], uniq) if uniq else (None, [])


def _parse_sl_tp(block: str) -> tuple[float | None, list[float]]:
    sl = None
    tps: list[float] = []
    in_tp = False
    for line in block.splitlines():
        low = line.lower()
        if SL_RE.search(low):
            base = re.split(r"\(|🎯|🛡", line)[0]
            base = re.sub(r"(?i)^\s*(sl|stop|стоп|стоп\s*лосс)\s*[:;\-.]?\s*", "", base)
            n = _first_number(base)
            if n is not None:
                sl = n

        if TP_RE.search(low):
            in_tp = True

        if TP_RE.search(low) or (in_tp and re.match(r"^\s*\d+[).]", line)):
            base = re.split(r"\(|🎯|🛡", line)[0]
            base = re.sub(r"(?i)^\s*[-—•]*\s*tp\s*\d*\s*[:;\-]?\s*", "", base)
            base = re.sub(r"^\s*\d+[).]\s*", "", base)
            n = _first_number(base)
            if n is not None:
                tps.append(n)

    return sl, tps


def _parse_allocations(block: str) -> tuple[list[float], list[str]]:
    pcts: list[float] = []
    fracs: list[str] = []
    for line in block.splitlines():
        low = line.lower()
        if TP_RE.search(low):
            continue
        for m in re.finditer(r"(\d[\d\s.,]*)\s*%", line):
            n = normalize_number(m.group(1))
            if n is not None:
                pcts.append(n)
        for m in re.finditer(r"\((\d+\s*/\s*\d+)\)", line):
            fracs.append(m.group(1).replace(" ", ""))
    return pcts, fracs


def parse_block(block: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    symbol = _extract_symbol(block)
    side = _extract_side(block.lower())
    sl, tps = _parse_sl_tp(block)
    entry, entries = _parse_entry(block, warnings)
    alloc_pcts, alloc_fracs = _parse_allocations(block)

    total_position_pct = None
    vals = [x for x in alloc_pcts if 0 < x <= 10]
    if vals:
        total_position_pct = max(vals)
    if total_position_pct is None and (entry or entries):
        total_position_pct = 1.0
        warnings.append("default total position percent applied: 1%")

    signal = {
        "symbol": symbol,
        "side": side,
        "entry": entry,
        "entries": entries,
        "sl": sl,
        "tps": tps,
        "total_position_pct": total_position_pct,
        "alloc_fracs": alloc_fracs,
    }

    required_ok = bool(symbol and side and sl is not None and entry is not None and tps)

    validation_conflict = False
    check_entries: list[float] = []
    if entry and entry.get("type") == "limit" and entry.get("price") is not None:
        check_entries.append(entry["price"])
    if entry and entry.get("type") == "zone":
        check_entries.extend([entry.get("price_min"), entry.get("price_max")])

    for ep in [x for x in check_entries if isinstance(x, (int, float))]:
        if side == "long" and not (sl < ep and all(tp > ep for tp in tps)):
            validation_conflict = True
        if side == "short" and not (sl > ep and all(tp < ep for tp in tps)):
            validation_conflict = True

    if validation_conflict:
        errors.append("directional validation conflict")

    if required_ok and not validation_conflict:
        status = "READY"
    elif symbol is None and side is None and entry is None and sl is None and not tps:
        status = "REJECT"
    else:
        status = "DRAFT"

    if status == "DRAFT" and not errors:
        errors.append("missing required fields or ambiguous parse")

    confidence = 0.95 if status == "READY" and not warnings else 0.8 if status == "READY" else 0.5 if status == "DRAFT" else 0.0
    return ParseResult(status=status, confidence=confidence, signal=signal if status != "REJECT" else None, errors=errors, warnings=warnings).to_dict()


def parse_text(text: str) -> list[dict[str, Any]]:
    return [parse_block(block) for block in split_setups(text)]


def load_fixture(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")



def split_blocks(text: str) -> list[str]:
    """Alias for v1 splitter name used by tests/spec wording."""
    return split_setups(text)
