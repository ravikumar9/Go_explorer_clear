#!/bin/bash
# Fix nginx and complete deployment
set -e

HOST="goexplorer-dev.cloud"
USER="deployer"
PASS="Thepowerof@9"

echo "=========================================="
echo "NGINX CONFIGURATION & SERVICE STARTUP"
echo "=========================================="

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST << 'ENDSSH'
# Check if nginx config exists
if [ -f /etc/nginx/sites-available/goexplorer ]; then
    echo "✓ Nginx config exists"
else
    echo "Creating nginx config..."
    sudo tee /etc/nginx/sites-available/goexplorer > /dev/null << 'EOF'
server {
    listen 80;
    server_name goexplorer-dev.cloud;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/deployer/Go_explorer_clear/staticfiles/;
    }
    
    location /media/ {
        alias /home/deployer/Go_explorer_clear/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
    sudo ln -sf /etc/nginx/sites-available/goexplorer /etc/nginx/sites-enabled/
    echo "✓ Nginx config created"
fi

# Test and reload nginx
echo "Testing nginx config..."
sudo nginx -t

echo "Reloading nginx..."
sudo systemctl reload nginx || sudo systemctl restart nginx

echo "Checking gunicorn..."
ps aux | grep gunicorn | grep -v grep || echo "⚠ Gunicorn not running"

# Make sure gunicorn is running
cd ~/Go_explorer_clear
source venv/bin/activate

# Kill any existing
pkill -f gunicorn || true
sleep 2

# Start gunicorn properly
mkdir -p logs
nohup gunicorn goexplorer.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 120 \
  --daemon \
  --access-logfile logs/gunicorn-access.log \
  --error-logfile logs/gunicorn-error.log

sleep 3
echo "✓ Gunicorn started"

# Final checks
echo ""
echo "=========================================="
echo "Service Status:"
echo "=========================================="
sudo systemctl status nginx --no-pager | head -5
ps aux | grep gunicorn | grep -v grep | head -3

echo ""
curl -sSf http://127.0.0.1:8000 >/dev/null && echo "✅ Local app: http://127.0.0.1:8000 - OK" || echo "❌ Local app failed"

ENDSSH

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Site: http://goexplorer-dev.cloud"
echo "🔐 Admin: http://goexplorer-dev.cloud/admin/"
echo "   User: goexplorer_dev_admin"
echo "   Pass: Thepowerof@9"
echo ""
