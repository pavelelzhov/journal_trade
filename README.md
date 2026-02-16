# journal_trade

Cloud journal skeleton v1.

## Components
- FastAPI: `src/api/main.py`
- DB models/session: `src/db/`
- Telegram bot (aiogram): `src/bot/bot.py`
- Parse worker: `src/worker/parse_worker.py`
- Deterministic parser: `src/parser.py`

## Local DB
```bash
docker compose up -d postgres
```

## Migrations
```bash
alembic upgrade head
```

## Run tests
```bash
pytest -vv
```

## Daily backup
```bash
./scripts/daily_backup.sh
```

Use cron for daily run (example in `docs/architecture_v1.md`).
