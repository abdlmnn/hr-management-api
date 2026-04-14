#!/usr/bin/env bash
# Run Celery worker + beat (same role as the `celery` service in docker-compose.yaml).
# Prerequisites: broker reachable (see CELERY_BROKER_URL in .env), database migrated.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -d "venv" ]]; then
  # shellcheck source=/dev/null
  source "venv/bin/activate"
elif [[ -d ".venv" ]]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-src.settings}"

CONCURRENCY="${CONCURRENCY:-2}"
WORKER_QUEUE="${WORKER_QUEUE:-celery}"
LOGLEVEL="${CELERY_LOGLEVEL:-info}"
WORKER_NAME="${CELERY_NODE_NAME:-celery@%h}"

exec celery -A src worker \
  --beat \
  --scheduler django \
  --loglevel="${LOGLEVEL}" \
  --concurrency="${CONCURRENCY}" \
  --pool=prefork \
  -n "${WORKER_NAME}" \
  -Q "${WORKER_QUEUE}"
