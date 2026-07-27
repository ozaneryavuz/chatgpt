#!/bin/sh
set -eu

umask 077

if [ "${ALO186_RESTORE_CONFIRM:-}" != "YES-RESTORE-ALO186-VERIFY" ]; then
  echo "ALO186_RESTORE_CONFIRM=YES-RESTORE-ALO186-VERIFY zorunludur." >&2
  exit 1
fi

required_vars="ALO186_RESTORE_DATABASE_URL RESTIC_REPOSITORY RESTIC_PASSWORD AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY"
for name in $required_vars; do
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    echo "$name zorunludur." >&2
    exit 1
  fi
done

if [ -n "${ALO186_DATABASE_URL:-}" ] && [ "$ALO186_RESTORE_DATABASE_URL" = "$ALO186_DATABASE_URL" ]; then
  echo "Restore doğrulama hedefi production veritabanıyla aynı olamaz." >&2
  exit 1
fi

RESTORE_URL=$(printf '%s' "$ALO186_RESTORE_DATABASE_URL" \
  | sed 's#^postgresql+psycopg://#postgresql://#' \
  | sed 's#^postgres://#postgresql://#')
WORK_DIR=$(mktemp -d /tmp/alo186-restore.XXXXXX)
cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT INT TERM

restic restore latest --tag alo186 --target "$WORK_DIR"
DUMP=$(find "$WORK_DIR" -type f -name 'alo186-*.dump' | sort | tail -n 1)
if [ -z "$DUMP" ]; then
  echo "Restic snapshot içinde PostgreSQL dump bulunamadı." >&2
  exit 1
fi

CHECKSUM="$DUMP.sha256"
if [ ! -f "$CHECKSUM" ]; then
  echo "Checksum dosyası bulunamadı: $CHECKSUM" >&2
  exit 1
fi
(
  cd "$(dirname "$DUMP")"
  sha256sum -c "$(basename "$CHECKSUM")"
)

pg_restore --list "$DUMP" >/dev/null
pg_restore --clean --if-exists --no-owner --no-privileges --dbname "$RESTORE_URL" "$DUMP"

psql "$RESTORE_URL" -v ON_ERROR_STOP=1 <<'SQL'
SELECT current_database() AS restored_database;
SELECT COUNT(*) AS alembic_version_rows FROM alembic_version;
SELECT COUNT(*) AS organization_count FROM organizations;
SELECT COUNT(*) AS user_count FROM users;
SQL

echo "ALO186 restore doğrulaması başarıyla tamamlandı: $DUMP"
