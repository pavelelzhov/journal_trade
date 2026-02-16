from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.parser import parse_block, split_setups


@dataclass
class RawMessageLike:
    id: int
    text: str


class WorkerRepository(Protocol):
    def fetch_unparsed_raw_messages(self, limit: int = 100) -> list[RawMessageLike]: ...

    def save_parsed_result(self, raw_message_id: int, result: dict) -> None: ...


def parse_once(repo: WorkerRepository, limit: int = 100) -> int:
    handled = 0
    for raw in repo.fetch_unparsed_raw_messages(limit=limit):
        blocks = split_setups(raw.text) or [raw.text]
        for block in blocks:
            result = parse_block(block)
            repo.save_parsed_result(raw.id, result)
            handled += 1
    return handled


def main() -> int:
    # real DB repository can be plugged in by deployment environment
    return 0


if __name__ == "__main__":
    print(f"Processed parsed signals: {main()}")
