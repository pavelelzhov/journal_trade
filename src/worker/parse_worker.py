from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from src.parser import parse_block, split_setups

if TYPE_CHECKING:
    from src.db.models import ParsedSignal, RawMessage, SignalStatus

PARSER_VERSION = "v1"


@dataclass
class RawMessageLike:
    id: int
    text: str


class WorkerRepository(Protocol):
    def fetch_unparsed_raw_messages(self, limit: int = 100) -> list[RawMessageLike]: ...

    def save_parsed_signal(
        self,
        raw_message_id: int,
        status: str,
        payload_json: dict,
        errors_json: list[str],
        warnings_json: list[str],
        parser_version: str,
    ) -> None: ...


def parse_once(repo: WorkerRepository, limit: int = 100) -> int:
    handled = 0
    for raw in repo.fetch_unparsed_raw_messages(limit=limit):
        blocks = split_setups(raw.text)
        if not blocks:
            blocks = [raw.text]

        for block in blocks:
            result = parse_block(block)
            repo.save_parsed_signal(
                raw_message_id=raw.id,
                status=result["status"],
                payload_json=result.get("signal") or {},
                errors_json=result.get("errors") or [],
                warnings_json=result.get("warnings") or [],
                parser_version=PARSER_VERSION,
            )
            handled += 1
    return handled


class SqlAlchemyWorkerRepository:
    def fetch_unparsed_raw_messages(self, limit: int = 100) -> list[RawMessageLike]:
        from src.db.models import ParsedSignal, RawMessage
        from src.db.session import SessionLocal

        with SessionLocal() as db:
            rows = (
                db.query(RawMessage)
                .outerjoin(ParsedSignal, ParsedSignal.raw_message_id == RawMessage.id)
                .filter(ParsedSignal.id.is_(None))
                .order_by(RawMessage.id.asc())
                .limit(limit)
                .all()
            )
            return [RawMessageLike(id=row.id, text=row.text) for row in rows]

    def save_parsed_signal(
        self,
        raw_message_id: int,
        status: str,
        payload_json: dict,
        errors_json: list[str],
        warnings_json: list[str],
        parser_version: str,
    ) -> None:
        from src.db.models import ParsedSignal, SignalStatus
        from src.db.session import SessionLocal

        with SessionLocal() as db:
            db.add(
                ParsedSignal(
                    raw_message_id=raw_message_id,
                    status=SignalStatus(status),
                    payload_json=payload_json,
                    errors_json=errors_json,
                    warnings_json=warnings_json,
                    parser_version=parser_version,
                )
            )
            db.commit()


def main() -> int:
    repo = SqlAlchemyWorkerRepository()
    return parse_once(repo)


if __name__ == "__main__":
    processed = main()
    print(f"Processed parsed signals: {processed}")
