#!/bin/sh
set -eu

normalize_database_url() {
  case "${ALO186_DATABASE_URL:-}" in
    postgresql://*)
      ALO186_DATABASE_URL="postgresql+psycopg://${ALO186_DATABASE_URL#postgresql://}"
      export ALO186_DATABASE_URL
      ;;
    postgres://*)
      ALO186_DATABASE_URL="postgresql+psycopg://${ALO186_DATABASE_URL#postgres://}"
      export ALO186_DATABASE_URL
      ;;
  esac
}

normalize_database_url
: "${ALO186_DATABASE_URL:?ALO186_DATABASE_URL zorunludur}"

alembic upgrade head
alembic check
python -m compileall -q app
python - <<'PY'
from app.config import settings
from app.db import check_db

assert settings.environment == "production", "Pre-deploy production ortamında çalışmalıdır."
assert settings.database_url.startswith("postgresql+psycopg://")
check_db()
print("ALO186 pre-deploy migration ve DB kontrolü başarılı.")
PY
