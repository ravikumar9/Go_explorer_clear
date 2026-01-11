#!/bin/bash
# COMPREHENSIVE STATIC FILES FIX SCRIPT
# Run this on the server to fix all static/media serving issues

set -e

echo "=================================="
echo "GOEXPLORER STATIC FILES FIX"
echo "=================================="
echo ""

PROJECT_ROOT="/home/deployer/Go_explorer_clear"
VENV_PATH="$PROJECT_ROOT/venv"

# Check if we're in the right place
if [ ! -f "$PROJECT_ROOT/manage.py" ]; then
    echo "❌ ERROR: Project not found at $PROJECT_ROOT"
    echo "   Edit this script and set PROJECT_ROOT correctly"
    exit 1
fi

echo "✓ Project found at $PROJECT_ROOT"
echo ""

# Step 1: Activate venv and collect static
echo "STEP 1: Collecting static files..."
cd "$PROJECT_ROOT"
source "$VENV_PATH/bin/activate"
python manage.py collectstatic --noinput --clear

echo "✓ Static files collected"
echo ""

# Step 2: Verify critical files exist
echo "STEP 2: Verifying critical files..."
REQUIRED_FILES=(
    "staticfiles/admin/css/base.css"
    "staticfiles/admin/css/login.css"
    "staticfiles/admin/js/theme.js"
    "staticfiles/css/booking-styles.css"
    "staticfiles/js/booking-utilities.js"
    "staticfiles/images/hotel_placeholder.svg"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(stat --format=%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        echo "✓ $file ($SIZE bytes)"
    else
        echo "❌ MISSING: $file"
        ALL_EXIST=false
    fi
done
echo ""

if [ "$ALL_EXIST" = false ]; then
    echo "❌ Some files missing! collectstatic may have failed."
    exit 1
fi

# Step 3: Fix permissions
echo "STEP 3: Fixing permissions..."
sudo chown -R www-data:www-data "$PROJECT_ROOT/staticfiles" "$PROJECT_ROOT/media"
sudo chmod -R 755 "$PROJECT_ROOT/staticfiles" "$PROJECT_ROOT/media"
echo "✓ Permissions fixed"
echo ""

# Step 4: Verify nginx can read files
echo "STEP 4: Verifying nginx can read static files..."
if sudo -u www-data test -r "$PROJECT_ROOT/staticfiles/admin/css/base.css"; then
    echo "✓ www-data can read static files"
else
    echo "❌ www-data CANNOT read static files (permissions issue)"
    exit 1
fi
echo ""

# Step 5: Update nginx config
echo "STEP 5: Updating nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/goexplorer"

if [ ! -f "$NGINX_CONF" ]; then
    echo "❌ Nginx config not found at $NGINX_CONF"
    echo "   Check your nginx installation"
    exit 1
fi

# Backup original
sudo cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%s)"
echo "✓ Backup created"

# Create new nginx config
sudo tee "$NGINX_CONF" > /dev/null <<'EOF'
server {
    listen 80;
    server_name goexplorer-dev.cloud;

    client_max_body_size 10M;

    # Static files - CRITICAL
    location /static/ {
        alias /home/deployer/Go_explorer_clear/staticfiles/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Media files
    location /media/ {
        alias /home/deployer/Go_explorer_clear/media/;
        access_log off;
        expires 7d;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Gunicorn timeout
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny hidden files
    location ~ /\. {
        deny all;
    }
}
EOF

echo "✓ Nginx config updated"
echo ""

# Step 6: Test nginx config
echo "STEP 6: Testing nginx configuration..."
if sudo nginx -t > /tmp/nginx_test.log 2>&1; then
    echo "✓ Nginx config is valid"
else
    echo "❌ Nginx config has errors:"
    cat /tmp/nginx_test.log
    exit 1
fi
echo ""

# Step 7: Reload nginx
echo "STEP 7: Reloading nginx..."
sudo systemctl reload nginx
echo "✓ Nginx reloaded"
echo ""

# Step 8: Restart gunicorn
echo "STEP 8: Restarting gunicorn..."
sudo systemctl restart gunicorn
echo "✓ Gunicorn restarted"
echo ""

# Step 9: Verify services
echo "STEP 9: Verifying services..."
if sudo systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
else
    echo "❌ Nginx is NOT running"
    exit 1
fi

if sudo systemctl is-active --quiet gunicorn; then
    echo "✓ Gunicorn is running"
else
    echo "❌ Gunicorn is NOT running"
    exit 1
fi
echo ""

# Step 10: Test static file serving
echo "STEP 10: Testing static file serving..."
echo ""
echo "Run these commands to verify static files are served:"
echo ""
echo "  curl -I http://goexplorer-dev.cloud/static/admin/css/base.css"
echo "  (Should return: HTTP/1.1 200 OK)"
echo ""
echo "  curl -I http://goexplorer-dev.cloud/media/packages/packages/1_primary.png"
echo "  (Should return: HTTP/1.1 200 OK)"
echo ""

echo "=================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Open incognito browser window"
echo "2. Go to: http://goexplorer-dev.cloud/admin/"
echo "3. Check:"
echo "   - Admin page is STYLED (blue header)"
echo "   - F12 Console shows ZERO 404 errors"
echo ""
echo "4. Test other pages:"
echo "   - http://goexplorer-dev.cloud/hotels/"
echo "   - http://goexplorer-dev.cloud/packages/"
echo ""
echo "5. If still broken, run diagnostics:"
echo "   sudo tail -50 /var/log/nginx/error.log"
echo "   sudo systemctl status gunicorn"
echo ""
