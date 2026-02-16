from __future__ import annotations

import json
from pathlib import Path

from src.parser import parse_block, split_setups


FIXTURE = Path("fixtures/setups_samples.txt")
GOLDEN_DIR = Path("tests/golden")


def test_parser_golden_blocks() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    blocks = split_setups(text)

    golden_files = sorted(GOLDEN_DIR.glob("block_*.json"))
    assert len(blocks) == len(golden_files), (
        f"Golden count mismatch: blocks={len(blocks)} golden={len(golden_files)}"
    )

    for idx, block in enumerate(blocks, start=1):
        expected_path = GOLDEN_DIR / f"block_{idx:03d}.json"
        assert expected_path.exists(), f"Missing golden file: {expected_path}"
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        actual = parse_block(block)
        assert actual == expected, f"Mismatch for {expected_path.name}"
