from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.parser import parse_block, split_setups


FIXTURE = Path("fixtures/setups_samples.txt")
GOLDEN_DIR = Path("tests/golden")
GOLDEN_FILES = sorted(GOLDEN_DIR.glob("block_*.json"))


def _block_index_from_file(path: Path) -> int:
    # Stable mapping: block_XXX.json -> blocks[XXX - 1]
    return int(path.stem.split("_")[1]) - 1


def _load_expected(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("expected_path", GOLDEN_FILES, ids=lambda p: p.name)
def test_parser_golden_each_file_is_separate_case(expected_path: Path) -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    blocks = split_setups(text)

    assert len(blocks) == len(GOLDEN_FILES), (
        f"Splitter/golden mismatch: blocks={len(blocks)} golden={len(GOLDEN_FILES)}"
    )

    block_index = _block_index_from_file(expected_path)
    assert 0 <= block_index < len(blocks), (
        f"Expected block index {block_index} for {expected_path.name}, but only {len(blocks)} blocks found"
    )

    actual = parse_block(blocks[block_index])
    expected = _load_expected(expected_path)

    # Strict ParseResult fields
    assert actual["status"] == expected["status"]
    assert actual["errors"] == expected["errors"]
    assert actual["warnings"] == expected["warnings"]

    actual_signal = actual.get("signal")
    expected_signal = expected.get("signal")
    assert (actual_signal is None) == (expected_signal is None)

    if expected_signal is not None:
        # Strict key fields inside signal
        signal_keys = [
            "symbol",
            "side",
            "entry",
            "entries",
            "sl",
            "tps",
            "total_position_pct",
            "alloc_fracs",
        ]
        for key in signal_keys:
            assert actual_signal.get(key) == expected_signal.get(key), (
                f"Mismatch in signal.{key} for {expected_path.name}"
            )
