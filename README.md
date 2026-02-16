# journal_trade

Cloud journal + deterministic parser + web UI demo.

## UI live at
https://paveleIzhov.github.io/journal_trade/

## How to run locally
```bash
cd web
npm i
npm run dev
```

Open: http://localhost:3000/journal_trade/dashboard

## Backend tests
```bash
python -m py_compile $(find src -name '*.py' -type f)
pytest -vv
```

## Daily backup
```bash
./scripts/daily_backup.sh
```
