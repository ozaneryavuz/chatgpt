#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

required=(
  ALO186_R2_ENDPOINT
  ALO186_R2_RESTIC_BUCKET
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  RESTIC_PASSWORD
)
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "$name zorunludur." >&2
    exit 1
  fi
done

export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-auto}
export RESTIC_REPOSITORY="s3:${ALO186_R2_ENDPOINT%/}/${ALO186_R2_RESTIC_BUCKET}"
TARGET_DIR=$(mktemp -d)
trap 'rm -rf "$TARGET_DIR"' EXIT INT TERM

SNAPSHOT=${1:-latest}
echo "Restic snapshot doğrulanıyor: $SNAPSHOT"
restic check
restic restore "$SNAPSHOT" --target "$TARGET_DIR"

DUMP_FILE=$(find "$TARGET_DIR" -type f -name 'alo186-*.dump' | sort | tail -n 1)
if [[ -z "$DUMP_FILE" ]]; then
  echo "Restore içinde PostgreSQL dump bulunamadı." >&2
  exit 1
fi

CHECKSUM_FILE="$DUMP_FILE.sha256"
if [[ ! -f "$CHECKSUM_FILE" ]]; then
  echo "Checksum dosyası bulunamadı: $CHECKSUM_FILE" >&2
  exit 1
fi

(
  cd "$(dirname "$DUMP_FILE")"
  sha256sum --check "$(basename "$CHECKSUM_FILE")"
)
pg_restore --list "$DUMP_FILE" >/dev/null

echo "Yedek okunabilir ve checksum geçerli: $(basename "$DUMP_FILE")"

if [[ -n "${ALO186_RESTORE_DATABASE_URL:-}" ]]; then
  if [[ "${ALO186_RESTORE_CONFIRM:-}" != "YES-RESTORE-ALO186" ]]; then
    echo "Tam restore için ALO186_RESTORE_CONFIRM=YES-RESTORE-ALO186 zorunludur." >&2
    exit 1
  fi
  RESTORE_URL=${ALO186_RESTORE_DATABASE_URL/postgresql+psycopg:\/\//postgresql:\/\/}
  RESTORE_URL=${RESTORE_URL/postgres:\/\//postgresql:\/\/}
  echo "Ayrı doğrulama veritabanına restore başlatılıyor..."
  pg_restore \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    --exit-on-error \
    --dbname="$RESTORE_URL" \
    "$DUMP_FILE"
  psql "$RESTORE_URL" -v ON_ERROR_STOP=1 -c 'SELECT 1;' >/dev/null
  echo "Tam restore doğrulaması başarılı."
else
  echo "Tam DB restore atlandı. ALO186_RESTORE_DATABASE_URL verilirse izole ortamda uygulanır."
fi
