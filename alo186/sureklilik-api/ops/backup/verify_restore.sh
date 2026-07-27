#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

required=(RESTIC_REPOSITORY RESTIC_PASSWORD AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY)
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "Zorunlu ortam değişkeni eksik: $name" >&2
    exit 2
  fi
done
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-auto}"

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
restic restore latest --host alo186-production --tag alo186 --target "$workdir"

dump="$(find "$workdir" -type f -name 'alo186-*.dump' | sort | tail -n1)"
checksum="${dump}.sha256"
if [[ -z "$dump" || ! -f "$dump" ]]; then
  echo "Restore içinde PostgreSQL dump bulunamadı." >&2
  exit 3
fi
if [[ ! -f "$checksum" ]]; then
  echo "Restore checksum dosyası bulunamadı: $checksum" >&2
  exit 4
fi
(
  cd "$(dirname "$dump")"
  sha256sum -c "$(basename "$checksum")"
)
pg_restore --list "$dump" >/dev/null

if [[ -n "${ALO186_RESTORE_DATABASE_URL:-}" ]]; then
  if [[ "${ALO186_RESTORE_CONFIRM:-}" != "RESTORE" ]]; then
    echo "Gerçek DB restore için ALO186_RESTORE_CONFIRM=RESTORE zorunludur." >&2
    exit 5
  fi
  case "$ALO186_RESTORE_DATABASE_URL" in
    postgresql+psycopg://*) TARGET_URL="postgresql://${ALO186_RESTORE_DATABASE_URL#postgresql+psycopg://}" ;;
    postgres://*) TARGET_URL="postgresql://${ALO186_RESTORE_DATABASE_URL#postgres://}" ;;
    *) TARGET_URL="$ALO186_RESTORE_DATABASE_URL" ;;
  esac
  pg_restore --dbname="$TARGET_URL" --clean --if-exists --no-owner --no-privileges "$dump"
fi

echo "ALO186 yedek restore doğrulaması başarılı: $(basename "$dump")"
