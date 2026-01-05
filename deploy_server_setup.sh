#!/bin/bash
# Deployment script for goexplorer-dev server
# Run this on the server as: bash deploy_server_setup.sh

set -e  # Exit on error

echo "=========================================="
echo "GoExplorer Dev Server Setup"
echo "=========================================="

# Navigate to project
cd ~/Go_explorer_clear

# Activate virtualenv
source venv/bin/activate

echo ""
echo "[1/6] Pulling latest code..."
git pull origin main

echo ""
echo "[2/6] Running Django system checks..."
python manage.py check

echo ""
echo "[3/6] Running migrations..."
python manage.py migrate --noinput

echo ""
echo "[4/6] Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "[5/6] Seeding development data..."
python manage.py seed_dev

echo ""
echo "[6/6] Restarting services..."
sudo systemctl restart gunicorn.goexplorer.service
sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Admin credentials:"
echo "  Username: goexplorer_dev_admin"
echo "  Password: Thepowerof@9"
echo ""
echo "Access the site at: https://goexplorer-dev.cloud"
echo ""
echo "Service status:"
sudo systemctl status gunicorn.goexplorer.service --no-pager | tail -5
echo ""
echo "Recent errors (if any):"
journalctl -u gunicorn.goexplorer -n 50 --no-pager | grep -i error || echo "No errors found"
