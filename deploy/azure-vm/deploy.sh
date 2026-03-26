#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/group_stock_project}"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="${VENV_DIR:-$APP_DIR/.venv}"
APP_USER="${APP_USER:-azureuser}"
APP_GROUP="${APP_GROUP:-www-data}"
SYSTEMD_SERVICE_NAME="${SYSTEMD_SERVICE_NAME:-group-stock-backend}"
NGINX_SITE_NAME="${NGINX_SITE_NAME:-group-stock}"
BACKEND_ENV_FILE="${BACKEND_ENV_FILE:-/etc/group-stock/backend.env}"

if [[ ! -f "$BACKEND_ENV_FILE" ]]; then
  echo "Missing backend env file: $BACKEND_ENV_FILE"
  exit 1
fi

sudo mkdir -p /etc/group-stock
sudo chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

pushd "$BACKEND_DIR" >/dev/null
set -a
source "$BACKEND_ENV_FILE"
set +a
python manage.py migrate
python manage.py collectstatic --noinput
popd >/dev/null

pushd "$FRONTEND_DIR" >/dev/null
npm ci
npm run build
popd >/dev/null

sudo cp "$APP_DIR/deploy/azure-vm/${SYSTEMD_SERVICE_NAME}.service" "/etc/systemd/system/${SYSTEMD_SERVICE_NAME}.service"
sudo cp "$APP_DIR/deploy/azure-vm/${NGINX_SITE_NAME}.conf" "/etc/nginx/sites-available/${NGINX_SITE_NAME}.conf"
sudo ln -sf "/etc/nginx/sites-available/${NGINX_SITE_NAME}.conf" "/etc/nginx/sites-enabled/${NGINX_SITE_NAME}.conf"
sudo rm -f /etc/nginx/sites-enabled/default

sudo systemctl daemon-reload
sudo systemctl enable "$SYSTEMD_SERVICE_NAME"
sudo systemctl restart "$SYSTEMD_SERVICE_NAME"
sudo nginx -t
sudo systemctl restart nginx

echo "Deployment complete."
echo "Backend service: sudo systemctl status ${SYSTEMD_SERVICE_NAME}"
echo "Nginx site: /etc/nginx/sites-available/${NGINX_SITE_NAME}.conf"
