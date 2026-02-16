# journal_trade

Cloud journal + deterministic parser + web UI demo.

## GitHub Pages
UI live at: https://pavelelzhov.github.io/journal_trade/

GitHub Pages for this repository is published from the `/docs` folder.

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
