#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

required=(ALO186_DATABASE_URL RESTIC_REPOSITORY RESTIC_PASSWORD AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY)
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "Zorunlu ortam değişkeni eksik: $name" >&2
    exit 2
  fi
done

case "$ALO186_DATABASE_URL" in
  postgresql+psycopg://*) DATABASE_URL="postgresql://${ALO186_DATABASE_URL#postgresql+psycopg://}" ;;
  postgres://*) DATABASE_URL="postgresql://${ALO186_DATABASE_URL#postgres://}" ;;
  *) DATABASE_URL="$ALO186_DATABASE_URL" ;;
esac
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-auto}"

heartbeat() {
  local suffix="${1:-}"
  if [[ -n "${ALO186_BACKUP_HEARTBEAT_URL:-}" ]]; then
    curl --fail --silent --show-error --max-time 15 \
      "${ALO186_BACKUP_HEARTBEAT_URL%/}${suffix}" >/dev/null || true
  fi
}

workdir="$(mktemp -d)"
cleanup() { rm -rf "$workdir"; }
failed() {
  local code="${1:-1}"
  trap - ERR
  heartbeat "/fail"
  echo "ALO186 R2/Restic yedeği başarısız oldu (exit=$code)." >&2
  exit "$code"
}
terminate() { exit 130; }
trap cleanup EXIT
trap 'failed $?' ERR
trap terminate INT TERM

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
dump="$workdir/alo186-$stamp.dump"
checksum="$dump.sha256"
metadata="$workdir/alo186-$stamp.json"
started_at="$(date +%s)"

pg_dump --dbname="$DATABASE_URL" --format=custom --compress=9 --no-owner --no-privileges --file="$dump"
pg_restore --list "$dump" >/dev/null
sha256sum "$dump" > "$checksum"
cat > "$metadata" <<JSON
{"schemaVersion":2,"createdAt":"$stamp","format":"pg_dump-custom","sha256":"$(cut -d' ' -f1 "$checksum")","source":"alo186-production","retention":{"daily":${ALO186_BACKUP_KEEP_DAILY:-14},"weekly":${ALO186_BACKUP_KEEP_WEEKLY:-8},"monthly":${ALO186_BACKUP_KEEP_MONTHLY:-12},"yearly":${ALO186_BACKUP_KEEP_YEARLY:-3}}}
JSON

if ! restic snapshots --json >/dev/null 2>&1; then
  echo "Restic deposu erişilemiyor veya henüz oluşturulmadı; init deneniyor."
  restic init
fi

restic backup "$dump" "$checksum" "$metadata" \
  --tag alo186 \
  --tag postgres \
  --tag production \
  --host alo186-production \
  --json

restic forget \
  --host alo186-production \
  --tag alo186 \
  --keep-daily "${ALO186_BACKUP_KEEP_DAILY:-14}" \
  --keep-weekly "${ALO186_BACKUP_KEEP_WEEKLY:-8}" \
  --keep-monthly "${ALO186_BACKUP_KEEP_MONTHLY:-12}" \
  --keep-yearly "${ALO186_BACKUP_KEEP_YEARLY:-3}" \
  --prune

# Her gece repository metadata kontrolü; pazar günü şifreli verinin %5'i okunur.
restic check
if [[ "$(date -u +%u)" == "7" ]]; then
  restic check --read-data-subset="1/20"
fi

ended_at="$(date +%s)"
size_bytes="$(stat -c '%s' "$dump")"
echo "ALO186 R2/Restic yedeği tamamlandı: stamp=$stamp bytes=$size_bytes duration_seconds=$((ended_at-started_at))"
heartbeat ""
