#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${ALO186_BACKUP_DIR:-./backups}"
RETENTION_DAYS="${ALO186_BACKUP_RETENTION_DAYS:-14}"
DATABASE_URL="${ALO186_DATABASE_URL:-}"

if [[ -n "${ALO186_DATABASE_URL_FILE:-}" ]]; then
  DATABASE_URL="$(tr -d '\r\n' < "$ALO186_DATABASE_URL_FILE")"
fi
if [[ -z "$DATABASE_URL" ]]; then
  echo "ALO186_DATABASE_URL veya ALO186_DATABASE_URL_FILE zorunludur." >&2
  exit 2
fi
if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump bulunamadı. PostgreSQL client araçlarını kurun." >&2
  exit 3
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR" || true
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$BACKUP_DIR/alo186-continuity-$stamp.dump"
temporary="$output.partial"

cleanup() {
  rm -f "$temporary"
}
trap cleanup EXIT

pg_dump --format=custom --compress=9 --no-owner --no-privileges --file="$temporary" "$DATABASE_URL"
mv "$temporary" "$output"
sha256sum "$output" > "$output.sha256"
chmod 600 "$output" "$output.sha256" || true

find "$BACKUP_DIR" -type f \( -name 'alo186-continuity-*.dump' -o -name 'alo186-continuity-*.dump.sha256' \) -mtime "+$RETENTION_DAYS" -delete

printf 'backup=%s\nchecksum=%s\n' "$output" "$output.sha256"
