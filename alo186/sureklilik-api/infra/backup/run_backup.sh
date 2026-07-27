#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

required=(
  ALO186_DATABASE_URL
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

DATABASE_URL=${ALO186_DATABASE_URL/postgresql+psycopg:\/\//postgresql:\/\/}
DATABASE_URL=${DATABASE_URL/postgres:\/\//postgresql:\/\/}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-auto}
export AWS_DEFAULT_REGION
export RESTIC_REPOSITORY="s3:${ALO186_R2_ENDPOINT%/}/${ALO186_R2_RESTIC_BUCKET}"

KEEP_DAILY=${ALO186_BACKUP_KEEP_DAILY:-14}
KEEP_WEEKLY=${ALO186_BACKUP_KEEP_WEEKLY:-8}
KEEP_MONTHLY=${ALO186_BACKUP_KEEP_MONTHLY:-12}
KEEP_YEARLY=${ALO186_BACKUP_KEEP_YEARLY:-3}
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
WORK_DIR=$(mktemp -d)
DUMP_FILE="$WORK_DIR/alo186-$TIMESTAMP.dump"
CHECKSUM_FILE="$DUMP_FILE.sha256"

heartbeat() {
  local suffix=${1:-}
  if [[ -n "${ALO186_BACKUP_HEARTBEAT_URL:-}" ]]; then
    curl --fail --silent --show-error --max-time 15 \
      "${ALO186_BACKUP_HEARTBEAT_URL%/}${suffix}" >/dev/null || true
  fi
}

cleanup() {
  rm -rf "$WORK_DIR"
}

failed() {
  local exit_code
  exit_code=${1:-1}
  trap - ERR
  heartbeat "/fail"
  echo "ALO186 backup başarısız oldu (exit=$exit_code)." >&2
  exit "$exit_code"
}

terminate() {
  exit 130
}

trap cleanup EXIT
trap 'failed $?' ERR
trap terminate INT TERM

if ! restic snapshots --compact >/dev/null 2>&1; then
  echo "Restic deposu erişilemiyor veya henüz oluşturulmadı; init deneniyor: $RESTIC_REPOSITORY"
  restic init
fi

started_at=$(date +%s)
echo "PostgreSQL mantıksal yedeği oluşturuluyor..."
pg_dump \
  --format=custom \
  --compress=9 \
  --no-owner \
  --no-privileges \
  --dbname="$DATABASE_URL" \
  --file="$DUMP_FILE"
sha256sum "$DUMP_FILE" > "$CHECKSUM_FILE"
pg_restore --list "$DUMP_FILE" >/dev/null

restic backup \
  --tag alo186 \
  --tag postgres \
  --tag production \
  "$DUMP_FILE" "$CHECKSUM_FILE"

restic forget \
  --tag alo186 \
  --keep-daily "$KEEP_DAILY" \
  --keep-weekly "$KEEP_WEEKLY" \
  --keep-monthly "$KEEP_MONTHLY" \
  --keep-yearly "$KEEP_YEARLY" \
  --prune

# Her çalışmada metadata; haftada bir daha pahalı veri alt kümesi kontrolü.
restic check
if [[ "$(date -u +%u)" == "7" ]]; then
  restic check --read-data-subset=1/20
fi

# Ayın ilk günü ayrı, retention-lock uygulanabilen vault bucket'a istemci tarafında
# şifrelenmiş dump kopyası. Restic parolasından ayrı anahtar hata alanını ayırır.
if [[ "$(date -u +%d)" == "01" && -n "${ALO186_R2_VAULT_BUCKET:-}" ]]; then
  if [[ -z "${ALO186_VAULT_ENCRYPTION_KEY:-}" ]]; then
    echo "ALO186_R2_VAULT_BUCKET kullanılıyorsa ALO186_VAULT_ENCRYPTION_KEY zorunludur." >&2
    exit 1
  fi
  vault_prefix="monthly/$(date -u +%Y)/$(date -u +%m)"
  vault_file="$DUMP_FILE.enc"
  vault_checksum="$vault_file.sha256"
  openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt \
    -in "$DUMP_FILE" \
    -out "$vault_file" \
    -pass env:ALO186_VAULT_ENCRYPTION_KEY
  sha256sum "$vault_file" > "$vault_checksum"
  aws --endpoint-url "$ALO186_R2_ENDPOINT" --region auto s3 cp \
    "$vault_file" "s3://${ALO186_R2_VAULT_BUCKET}/${vault_prefix}/$(basename "$vault_file")" \
    --only-show-errors
  aws --endpoint-url "$ALO186_R2_ENDPOINT" --region auto s3 cp \
    "$vault_checksum" "s3://${ALO186_R2_VAULT_BUCKET}/${vault_prefix}/$(basename "$vault_checksum")" \
    --only-show-errors
fi

ended_at=$(date +%s)
size_bytes=$(stat -c '%s' "$DUMP_FILE")
echo "ALO186 backup tamamlandı: bytes=$size_bytes duration_seconds=$((ended_at-started_at))"
heartbeat ""
