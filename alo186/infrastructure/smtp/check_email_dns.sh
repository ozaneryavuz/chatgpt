#!/usr/bin/env bash
set -Eeuo pipefail

DOMAIN=${1:-alo186.com}
FAILED=0

check_contains() {
  local label=$1
  local value=$2
  local expected=$3
  if grep -qi -- "$expected" <<<"$value"; then
    echo "OK  $label"
  else
    echo "FAIL $label — '$expected' bulunamadı" >&2
    FAILED=1
  fi
}

SPF=$(dig +short TXT "$DOMAIN" | tr -d '"' | grep -i 'v=spf1' || true)
DMARC=$(dig +short TXT "_dmarc.$DOMAIN" | tr -d '"' || true)

check_contains "SPF" "$SPF" "v=spf1"
check_contains "DMARC" "$DMARC" "v=DMARC1"

if [[ -n "${POSTMARK_DKIM_HOST:-}" ]]; then
  DKIM=$(dig +short TXT "$POSTMARK_DKIM_HOST" | tr -d '"' || true)
  check_contains "Postmark DKIM ($POSTMARK_DKIM_HOST)" "$DKIM" "v=DKIM1"
fi

if [[ -n "${POSTMARK_RETURN_PATH_HOST:-}" ]]; then
  RETURN_PATH=$(dig +short CNAME "$POSTMARK_RETURN_PATH_HOST" || true)
  if [[ -n "$RETURN_PATH" ]]; then
    echo "OK  Postmark Return-Path ($POSTMARK_RETURN_PATH_HOST → $RETURN_PATH)"
  else
    echo "FAIL Postmark Return-Path CNAME bulunamadı: $POSTMARK_RETURN_PATH_HOST" >&2
    FAILED=1
  fi
fi

if [[ $(grep -oi 'v=spf1' <<<"$SPF" | wc -l | tr -d ' ') -gt 1 ]]; then
  echo "FAIL Birden fazla SPF kaydı algılandı; tek kayıt halinde birleştirin." >&2
  FAILED=1
fi

exit "$FAILED"
