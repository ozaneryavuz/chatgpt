#!/bin/sh
set -eu

if [ "${ALO186_RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

exec "$@"
