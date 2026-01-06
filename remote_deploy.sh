#!/bin/bash
# Execute deployment on remote server
set -e

HOST="goexplorer-dev.cloud"
USER="deployer"
PASS="Thepowerof@9"

echo "=========================================="
echo "REMOTE DEPLOYMENT TO $HOST"
echo "=========================================="

# Create deployment script on server and execute it
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST << 'ENDSSH'
cd ~/Go_explorer_clear
source venv/bin/activate

echo "[1/8] Pulling latest code..."
git pull origin main

echo "[2/8] Installing dependencies..."
pip install -q -r requirements.txt

echo "[3/8] Django system check..."
python manage.py check

echo "[4/8] Running migrations..."
python manage.py migrate --noinput

echo "[5/8] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[6/8] Cleaning and reseeding database..."
python manage.py clean_and_reseed

echo "[7/8] Managing services..."
# Kill any existing gunicorn processes
pkill -f gunicorn || true
sleep 2

# Start gunicorn
cd ~/Go_explorer_clear
source venv/bin/activate
nohup gunicorn goexplorer.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile logs/gunicorn-access.log \
  --error-logfile logs/gunicorn-error.log \
  --daemon

# Restart nginx
sudo systemctl reload nginx

echo "[8/8] Verifying..."
sleep 3
curl -sSf http://127.0.0.1:8000 >/dev/null && echo "✅ App running" || echo "❌ App failed"

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo "Admin: https://goexplorer-dev.cloud/admin/"
echo "User: goexplorer_dev_admin / Thepowerof@9"
ENDSSH

echo ""
echo "=========================================="
echo "✅ REMOTE DEPLOYMENT FINISHED"
echo "=========================================="
echo ""
echo "Checking public site..."
sleep 5
curl -sSf https://goexplorer-dev.cloud >/dev/null && echo "✅ Site is LIVE at https://goexplorer-dev.cloud" || echo "⚠ Site check failed - may need DNS/nginx config"
