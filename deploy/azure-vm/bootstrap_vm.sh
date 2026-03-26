#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/group_stock_project}"
APP_USER="${APP_USER:-azureuser}"
APP_GROUP="${APP_GROUP:-www-data}"
PYTHON_VERSION="${PYTHON_VERSION:-python3}"
NODE_SETUP_MAJOR="${NODE_SETUP_MAJOR:-20}"

sudo apt-get update
sudo apt-get install -y \
  nginx \
  postgresql \
  postgresql-contrib \
  python3-venv \
  python3-pip \
  build-essential \
  libpq-dev \
  curl \
  git

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL "https://deb.nodesource.com/setup_${NODE_SETUP_MAJOR}.x" | sudo -E bash -
  sudo apt-get install -y nodejs
fi

sudo mkdir -p "$APP_DIR"
sudo chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"

echo "VM bootstrap complete."
echo "Next:"
echo "1. Copy the repository into $APP_DIR"
echo "2. Copy backend.env.example to /etc/group-stock/backend.env and edit it"
echo "3. Run deploy/azure-vm/deploy.sh from inside the repo"
