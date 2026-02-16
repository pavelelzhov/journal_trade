from __future__ import annotations

from dataclasses import dataclass

from src.worker.parse_worker import RawMessageLike, parse_once


@dataclass
class _Saved:
    raw_message_id: int
    result: dict


class _FakeRepo:
    def __init__(self, messages: list[RawMessageLike]) -> None:
        self._messages = messages
        self.saved: list[_Saved] = []

    def fetch_unparsed_raw_messages(self, limit: int = 100) -> list[RawMessageLike]:
        return self._messages[:limit]

    def save_parsed_result(self, raw_message_id: int, result: dict) -> None:
        self.saved.append(_Saved(raw_message_id=raw_message_id, result=result))


def test_worker_parses_raw_message_into_result() -> None:
    text = "$BTCUSDT - SHORT\nВход лимитка 67900\nStop 68700\nTейк-профит\n1) 67000"
    repo = _FakeRepo([RawMessageLike(id=1, text=text)])

    processed = parse_once(repo)

    assert processed == 1
    assert len(repo.saved) == 1
    saved = repo.saved[0]
    assert saved.raw_message_id == 1
    assert saved.result["signal"]["symbol"] == "BTCUSDT"
