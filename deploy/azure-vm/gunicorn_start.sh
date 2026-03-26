#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/group_stock_project}"
VENV_DIR="${VENV_DIR:-$APP_DIR/.venv}"
BACKEND_DIR="${BACKEND_DIR:-$APP_DIR/backend}"
BIND_ADDR="${BIND_ADDR:-127.0.0.1:8000}"
WORKERS="${GUNICORN_WORKERS:-3}"
TIMEOUT="${GUNICORN_TIMEOUT:-180}"

source "$VENV_DIR/bin/activate"
cd "$BACKEND_DIR"

exec gunicorn \
  --workers "$WORKERS" \
  --bind "$BIND_ADDR" \
  --timeout "$TIMEOUT" \
  --access-logfile - \
  --error-logfile - \
  config.wsgi:application
