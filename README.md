# journal_trade

Cloud journal + deterministic parser + UI demo.

## UI Demo link
After enabling GitHub Pages for this repository, the demo is published at:

`https://<org-or-user>.github.io/<repo>/`

(For this repo name: `journal_trade` -> `https://<org-or-user>.github.io/journal_trade/`)

## How to run locally
```bash
# backend stack (optional for API mode)
docker compose up -d postgres api

# UI demo
cd web
npm install
npm run dev
```

Open http://localhost:3000

- Default mode is **Demo** (reads `/public/demo/*.json`)
- Switch to **API** mode in the header to call backend via `NEXT_PUBLIC_API_BASE_URL`

## Backend tests
```bash
python -m py_compile $(find src -name '*.py' -type f)
pytest -vv
```

## Daily backup
```bash
./scripts/daily_backup.sh
```
