#!/bin/sh
set -eu

umask 077

required_vars="ALO186_DATABASE_URL RESTIC_REPOSITORY RESTIC_PASSWORD AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY"
for name in $required_vars; do
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    echo "$name zorunludur." >&2
    exit 1
  fi
done

DATABASE_URL=$(printf '%s' "$ALO186_DATABASE_URL" \
  | sed 's#^postgresql+psycopg://#postgresql://#' \
  | sed 's#^postgres://#postgresql://#')

KEEP_DAILY=${ALO186_BACKUP_KEEP_DAILY:-14}
KEEP_WEEKLY=${ALO186_BACKUP_KEEP_WEEKLY:-8}
KEEP_MONTHLY=${ALO186_BACKUP_KEEP_MONTHLY:-12}
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
WORK_DIR=$(mktemp -d /tmp/alo186-backup.XXXXXX)
DUMP="$WORK_DIR/alo186-$TIMESTAMP.dump"
CHECKSUM="$DUMP.sha256"
MANIFEST="$WORK_DIR/manifest.json"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT INT TERM

pg_dump --format=custom --compress=9 --no-owner --no-privileges "$DATABASE_URL" > "$DUMP"
sha256sum "$DUMP" > "$CHECKSUM"

cat > "$MANIFEST" <<EOF
{"service":"alo186-continuity","created_at":"$TIMESTAMP","postgres_format":"custom","checksum":"sha256","retention":{"daily":$KEEP_DAILY,"weekly":$KEEP_WEEKLY,"monthly":$KEEP_MONTHLY}}
EOF

if ! restic snapshots >/dev/null 2>&1; then
  restic init
fi

restic backup --tag alo186 --tag postgres --host alo186-render "$DUMP" "$CHECKSUM" "$MANIFEST"
restic forget \
  --tag alo186 \
  --keep-daily "$KEEP_DAILY" \
  --keep-weekly "$KEEP_WEEKLY" \
  --keep-monthly "$KEEP_MONTHLY" \
  --prune
restic check

echo "ALO186 PostgreSQL yedeği R2/Restic deposuna gönderildi: $TIMESTAMP"
