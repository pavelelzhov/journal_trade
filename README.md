# journal_trade

Prod v1 vertical slice: UI + API + DB + RBAC.

## Run (docker)
```bash
docker compose up -d postgres api web
```

## Migrations
```bash
alembic upgrade head
```

## Tests
```bash
pytest -q
```
