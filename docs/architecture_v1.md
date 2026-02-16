# Cloud Journal Skeleton v1

## Flow
1. **Telegram Bot** receives raw text message.
2. Bot stores message in **RawMessage**.
3. **Worker** reads new RawMessage rows, calls deterministic parser (`split_setups`, `parse_block`) and writes **ParsedSignal**.
4. API reads from **ParsedSignal/Trade** and exposes filters/exports/imports.

## Components
- `src/bot/bot.py` — Telegram intake channel.
- `src/worker/parse_worker.py` — deterministic parsing worker.
- `src/api/main.py` — FastAPI endpoints.
- `src/db/models.py` — SQLAlchemy data model.
- `docker-compose.yml` — local Postgres.

## RBAC
- `ADMIN`: can access all traders.
- `TRADER`: can access only own records.

## Backup
Daily backup script: `scripts/daily_backup.sh`

Example cron (daily at 02:00):
```bash
0 2 * * * cd /path/to/repo && ./scripts/daily_backup.sh
```
