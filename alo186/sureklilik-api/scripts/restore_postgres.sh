#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Kullanım: $0 /backups/alo186-YYYYMMDDTHHMMSSZ.dump" >&2
  exit 1
fi
if [ -n "${ALO186_DATABASE_URL_FILE:-}" ]; then
  if [ -n "${ALO186_DATABASE_URL:-}" ]; then
    echo "ALO186_DATABASE_URL ve ALO186_DATABASE_URL_FILE aynı anda kullanılamaz." >&2
    exit 1
  fi
  ALO186_DATABASE_URL=$(cat "$ALO186_DATABASE_URL_FILE")
fi
if [ -z "${ALO186_DATABASE_URL:-}" ]; then
  echo "ALO186_DATABASE_URL veya ALO186_DATABASE_URL_FILE zorunludur." >&2
  exit 1
fi

BACKUP_FILE=$1
CHECKSUM_FILE="$BACKUP_FILE.sha256"
DATABASE_URL=$(printf '%s' "$ALO186_DATABASE_URL" | sed 's#postgresql+psycopg://#postgresql://#')

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Yedek dosyası bulunamadı: $BACKUP_FILE" >&2
  exit 1
fi
if [ -f "$CHECKSUM_FILE" ]; then
  (cd "$(dirname "$BACKUP_FILE")" && sha256sum -c "$(basename "$CHECKSUM_FILE")")
else
  echo "Uyarı: checksum dosyası bulunamadı." >&2
fi

if [ "${ALO186_RESTORE_CONFIRM:-}" != "YES-RESTORE-ALO186" ]; then
  echo "Geri yükleme yıkıcıdır. ALO186_RESTORE_CONFIRM=YES-RESTORE-ALO186 ayarlayın." >&2
  exit 1
fi

pg_restore --clean --if-exists --no-owner --no-privileges --dbname "$DATABASE_URL" "$BACKUP_FILE"
echo "Geri yükleme tamamlandı: $BACKUP_FILE"
