#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Kullanım: $0 <backup.dump>" >&2
  exit 2
fi

backup="$1"
checksum="$backup.sha256"
DATABASE_URL="${ALO186_DATABASE_URL:-}"

if [[ -n "${ALO186_DATABASE_URL_FILE:-}" ]]; then
  DATABASE_URL="$(tr -d '\r\n' < "$ALO186_DATABASE_URL_FILE")"
fi
if [[ -z "$DATABASE_URL" ]]; then
  echo "ALO186_DATABASE_URL veya ALO186_DATABASE_URL_FILE zorunludur." >&2
  exit 3
fi
if [[ ! -f "$backup" || ! -f "$checksum" ]]; then
  echo "Backup veya checksum dosyası bulunamadı." >&2
  exit 4
fi
if ! command -v pg_restore >/dev/null 2>&1; then
  echo "pg_restore bulunamadı. PostgreSQL client araçlarını kurun." >&2
  exit 5
fi

sha256sum --check "$checksum"

if [[ "${ALO186_RESTORE_CONFIRM:-}" != "RESTORE" ]]; then
  echo "Geri yükleme yıkıcıdır. ALO186_RESTORE_CONFIRM=RESTORE ayarlayın." >&2
  exit 6
fi

pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --exit-on-error \
  --dbname="$DATABASE_URL" \
  "$backup"

echo "Geri yükleme tamamlandı: $backup"
