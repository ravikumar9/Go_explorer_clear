#!/bin/bash
# Complete server setup and deployment script
set -e

echo "=========================================="
echo "DEPLOYING TO goexplorer-dev.cloud"
echo "=========================================="

cd ~/Go_explorer_clear
source venv/bin/activate

echo ""
echo "[1/8] Pulling latest code..."
git pull origin main

echo ""
echo "[2/8] Installing/updating dependencies..."
pip install -q -r requirements.txt

echo ""
echo "[3/8] Running Django checks..."
python manage.py check

echo ""
echo "[4/8] Running migrations..."
python manage.py migrate --noinput

echo ""
echo "[5/8] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo ""
echo "[6/8] Cleaning and reseeding database..."
python manage.py clean_and_reseed

echo ""
echo "[7/8] Finding and restarting services..."
# Check which gunicorn service exists
if systemctl list-units --full -all | grep -q "gunicorn.service"; then
    echo "Restarting gunicorn.service..."
    sudo systemctl restart gunicorn.service
elif systemctl list-units --full -all | grep -q "gunicorn"; then
    SERVICE=$(systemctl list-units --full -all | grep gunicorn | awk '{print $1}' | head -1)
    echo "Restarting $SERVICE..."
    sudo systemctl restart $SERVICE
else
    echo "⚠ Gunicorn service not found - starting manually..."
    pkill -f gunicorn || true
    cd ~/Go_explorer_clear
    source venv/bin/activate
    gunicorn goexplorer.wsgi:application --bind 127.0.0.1:8000 --workers 3 --daemon
fi

# Reload nginx
echo "Reloading nginx..."
sudo systemctl reload nginx || sudo systemctl restart nginx

echo ""
echo "[8/8] Verifying deployment..."
sleep 3
curl -sSf http://127.0.0.1:8000 > /dev/null && echo "✅ Local server responding" || echo "❌ Local server not responding"
curl -sSf https://goexplorer-dev.cloud > /dev/null && echo "✅ Public site responding" || echo "⚠ Public site check failed"

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🔐 Admin Access:"
echo "   URL: https://goexplorer-dev.cloud/admin/"
echo "   User: goexplorer_dev_admin"
echo "   Pass: Thepowerof@9"
echo ""
echo "📊 Site: https://goexplorer-dev.cloud"
echo ""
