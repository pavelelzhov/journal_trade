# journal_trade

Cloud journal skeleton v1 + Top Journal UI v1.

## Run locally
```bash
docker compose up -d postgres

docker compose up api web
```

- API: http://localhost:8000
- Web: http://localhost:3000

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
