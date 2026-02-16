from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.parser import parse_block, split_setups


FIXTURE = Path("fixtures/setups_samples.txt")
GOLDEN_DIR = Path("tests/golden")
TOTAL_CASES = 15


def _load_expected(index: int) -> dict:
    path = GOLDEN_DIR / f"block_{index:03d}.json"
    assert path.exists(), f"Missing golden file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("index", range(1, TOTAL_CASES + 1))
def test_parser_golden_first_15_blocks(index: int) -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    blocks = split_setups(text)
    assert len(blocks) >= TOTAL_CASES, f"Expected at least {TOTAL_CASES} blocks, got {len(blocks)}"

    actual = parse_block(blocks[index - 1])
    expected = _load_expected(index)

    assert actual["status"] == expected["status"]
    assert actual["signal"] == expected["signal"]
    assert actual["errors"] == expected["errors"]
    assert actual["warnings"] == expected["warnings"]
