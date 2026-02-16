from __future__ import annotations

from dataclasses import dataclass

from src.worker.parse_worker import RawMessageLike, parse_once


@dataclass
class _SavedSignal:
    raw_message_id: int
    status: str
    payload_json: dict
    errors_json: list[str]
    warnings_json: list[str]
    parser_version: str


class _FakeRepo:
    def __init__(self, messages: list[RawMessageLike]) -> None:
        self._messages = messages
        self.saved: list[_SavedSignal] = []

    def fetch_unparsed_raw_messages(self, limit: int = 100) -> list[RawMessageLike]:
        return self._messages[:limit]

    def save_parsed_signal(
        self,
        raw_message_id: int,
        status: str,
        payload_json: dict,
        errors_json: list[str],
        warnings_json: list[str],
        parser_version: str,
    ) -> None:
        self.saved.append(
            _SavedSignal(
                raw_message_id=raw_message_id,
                status=status,
                payload_json=payload_json,
                errors_json=errors_json,
                warnings_json=warnings_json,
                parser_version=parser_version,
            )
        )


def test_worker_parses_raw_message_into_parsed_signal() -> None:
    text = "$BTCUSDT - SHORT\nВход лимитка 67900\nStop 68700\nTейк-профит\n1) 67000"
    repo = _FakeRepo([RawMessageLike(id=1, text=text)])

    processed = parse_once(repo)

    assert processed == 1
    assert len(repo.saved) == 1
    saved = repo.saved[0]
    assert saved.raw_message_id == 1
    assert saved.status in {"READY", "DRAFT", "REJECT"}
    assert saved.payload_json.get("symbol") == "BTCUSDT"
    assert saved.parser_version == "v1"
