#!/bin/sh
set -eu

umask 077

if [ -z "${ALO186_DATABASE_URL:-}" ]; then
  echo "ALO186_DATABASE_URL zorunludur." >&2
  exit 1
fi

DATABASE_URL=$(printf '%s' "$ALO186_DATABASE_URL" | sed 's#postgresql+psycopg://#postgresql://#')
BACKUP_DIR=${ALO186_BACKUP_DIR:-/backups}
RETENTION_DAYS=${ALO186_BACKUP_RETENTION_DAYS:-14}
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$BACKUP_DIR"

TARGET="$BACKUP_DIR/alo186-$TIMESTAMP.dump"
TEMP="$TARGET.tmp"

cleanup() {
  rm -f "$TEMP"
}
trap cleanup EXIT INT TERM

pg_dump --format=custom --compress=9 --no-owner --no-privileges "$DATABASE_URL" > "$TEMP"
mv "$TEMP" "$TARGET"
sha256sum "$TARGET" > "$TARGET.sha256"

find "$BACKUP_DIR" -type f \( -name 'alo186-*.dump' -o -name 'alo186-*.dump.sha256' \) -mtime "+$RETENTION_DAYS" -delete

if command -v restic >/dev/null 2>&1 && [ -n "${RESTIC_REPOSITORY:-}" ]; then
  restic backup "$TARGET" "$TARGET.sha256"
  restic forget --keep-daily 7 --keep-weekly 8 --keep-monthly 12 --prune
fi

echo "Yedek oluşturuldu: $TARGET"
