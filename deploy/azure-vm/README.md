# Azure VM Deployment

These files prepare the project for a standard Ubuntu-based Azure VM deployment with:

- `Nginx` serving the built React frontend
- `Gunicorn` running Django on `127.0.0.1:8000`
- `systemd` keeping the backend alive
- PostgreSQL on the VM

## Assumptions

- VM OS: Ubuntu 22.04 or similar
- Repo path on VM: `/opt/group_stock_project`
- Linux user running the app: `azureuser`
- Backend env file: `/etc/group-stock/backend.env`
- Frontend is built statically and served by Nginx

## Files

- `bootstrap_vm.sh`: installs OS packages like Python, Node, Nginx, and PostgreSQL
- `deploy.sh`: installs Python and Node dependencies, runs migrations, builds frontend, and enables services
- `gunicorn_start.sh`: starts Django with Gunicorn
- `group-stock-backend.service`: systemd service for Django
- `group-stock.conf`: Nginx site config
- `backend.env.example`: production backend environment template
- `frontend.env.example`: frontend environment template

## First-time setup

1. Copy the repo to the VM:

```bash
sudo mkdir -p /opt/group_stock_project
sudo chown -R azureuser:www-data /opt/group_stock_project
git clone <your-repo-url> /opt/group_stock_project
cd /opt/group_stock_project
```

2. Bootstrap the VM:

```bash
chmod +x deploy/azure-vm/bootstrap_vm.sh
./deploy/azure-vm/bootstrap_vm.sh
```

3. Create the backend env file:

```bash
sudo mkdir -p /etc/group-stock
sudo cp deploy/azure-vm/backend.env.example /etc/group-stock/backend.env
sudo nano /etc/group-stock/backend.env
```

4. Create the frontend env file:

```bash
cp deploy/azure-vm/frontend.env.example frontend/.env
nano frontend/.env
```

5. Deploy:

```bash
chmod +x deploy/azure-vm/deploy.sh deploy/azure-vm/gunicorn_start.sh
APP_DIR=/opt/group_stock_project ./deploy/azure-vm/deploy.sh
```

## PostgreSQL quick start

```bash
sudo -u postgres psql
CREATE DATABASE stock_analytics_db;
CREATE USER stockapp WITH PASSWORD 'replace-with-db-password';
ALTER ROLE stockapp SET client_encoding TO 'utf8';
ALTER ROLE stockapp SET default_transaction_isolation TO 'read committed';
ALTER ROLE stockapp SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE stock_analytics_db TO stockapp;
\q
```

## SSL

This setup starts with HTTP on port 80. For HTTPS, install Certbot after the base deployment:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

If you enable HTTPS, update:

- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `VITE_API_BASE_URL`

## Useful commands

```bash
sudo systemctl status group-stock-backend
sudo journalctl -u group-stock-backend -f
sudo nginx -t
sudo systemctl reload nginx
```
