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

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
dump="$workdir/alo186-$stamp.dump"
checksum="$dump.sha256"
metadata="$workdir/alo186-$stamp.json"

pg_dump --dbname="$DATABASE_URL" --format=custom --compress=9 --no-owner --no-privileges --file="$dump"
pg_restore --list "$dump" >/dev/null
sha256sum "$dump" > "$checksum"
cat > "$metadata" <<JSON
{"schemaVersion":1,"createdAt":"$stamp","format":"pg_dump-custom","sha256":"$(cut -d' ' -f1 "$checksum")","source":"alo186-production"}
JSON

if ! restic snapshots --json >/dev/null 2>&1; then
  restic init
fi

restic backup "$dump" "$checksum" "$metadata" \
  --tag alo186 \
  --tag postgres \
  --host alo186-production \
  --json

restic forget \
  --host alo186-production \
  --tag alo186 \
  --keep-daily "${ALO186_BACKUP_KEEP_DAILY:-14}" \
  --keep-weekly "${ALO186_BACKUP_KEEP_WEEKLY:-8}" \
  --keep-monthly "${ALO186_BACKUP_KEEP_MONTHLY:-12}" \
  --prune

restic check --read-data-subset="1/20"
echo "ALO186 R2/Restic yedeği başarıyla tamamlandı: $stamp"
