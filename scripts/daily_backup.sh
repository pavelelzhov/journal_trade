#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

TS="$(date +%F_%H-%M-%S)"
OUT_FILE="$BACKUP_DIR/journal_${TS}.sql"

: "${PGHOST:=localhost}"
: "${PGPORT:=5432}"
: "${PGUSER:=postgres}"
: "${PGDATABASE:=journal}"

pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" > "$OUT_FILE"
echo "Backup created: $OUT_FILE"
