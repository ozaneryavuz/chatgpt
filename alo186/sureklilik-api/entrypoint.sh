#!/bin/sh
set -eu

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

if [ "${ALO186_RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

exec "$@"
