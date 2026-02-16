from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.parser import parse_block, split_setups

FIXTURE = Path("fixtures/setups_samples.txt")
GOLDEN_DIR = Path("tests/golden")


def _load_blocks_and_golden() -> tuple[list[str], list[Path]]:
    text = FIXTURE.read_text(encoding="utf-8")
    blocks = split_setups(text)

    golden_files = sorted(GOLDEN_DIR.glob("block_*.json"))
    assert len(golden_files) > 0, "No golden files found in tests/golden/"
    assert len(blocks) == len(golden_files), (
        f"Golden count mismatch: blocks={len(blocks)} golden={len(golden_files)}"
    )
    return blocks, golden_files


BLOCKS, GOLDEN_FILES = _load_blocks_and_golden()


@pytest.mark.parametrize(
    "i",
    range(len(GOLDEN_FILES)),
    ids=lambda i: GOLDEN_FILES[i].name,
)
def test_parser_golden_block(i: int) -> None:
    expected_path = GOLDEN_FILES[i]
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    actual = parse_block(BLOCKS[i])

    assert actual == expected, f"Mismatch for {expected_path.name}"
