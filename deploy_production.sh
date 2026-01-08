#!/bin/bash
# ============================================================================
# GOEXPLORER PRODUCTION DEPLOYMENT SCRIPT
# Fixes 502 Bad Gateway and deploys application with Gunicorn + Nginx
# Usage: ./deploy_production.sh
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GoExplorer Production Deployment (502 Fix)             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# ============================================================================
# SECTION 1: LOCAL VALIDATION
# ============================================================================
echo -e "\n${YELLOW}[LOCAL] Validating project structure...${NC}"

if [ ! -f "manage.py" ]; then
    echo -e "${RED}✗ ERROR: manage.py not found. Run from project root!${NC}"
    exit 1
fi

if [ ! -f "goexplorer/wsgi.py" ]; then
    echo -e "${RED}✗ ERROR: goexplorer/wsgi.py not found!${NC}"
    exit 1
fi

if [ ! -f "deploy/gunicorn.goexplorer.service" ]; then
    echo -e "${RED}✗ ERROR: deploy/gunicorn.goexplorer.service not found!${NC}"
    exit 1
fi

if [ ! -f "deploy/nginx.goexplorer.dev.conf" ]; then
    echo -e "${RED}✗ ERROR: deploy/nginx.goexplorer.dev.conf not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project structure valid${NC}"

# ============================================================================
# SECTION 2: GIT COMMIT & PUSH (if needed)
# ============================================================================
echo -e "\n${YELLOW}[GIT] Committing deployment fixes...${NC}"

git add deploy/gunicorn.goexplorer.service deploy/nginx.goexplorer.dev.conf
git commit -m "Fix: Update Gunicorn systemd service and Nginx config to resolve 502 Bad Gateway

- Ensure Gunicorn creates socket at /run/gunicorn-goexplorer/goexplorer.sock
- Pre-create socket directory with proper permissions
- Add upstream block to Nginx for cleaner proxy config
- Improve timeout and error handling
- Update service dependencies and restart policy" || echo "No changes to commit"

git push origin main

echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"

# ============================================================================
# SECTION 3: SERVER DEPLOYMENT (SSH)
# ============================================================================
SERVER_HOST="goexplorer-dev.cloud"
SERVER_USER="deployer"
PROJECT_PATH="/home/deployer/goexplorer"

echo -e "\n${YELLOW}[SERVER] Connecting to ${SERVER_HOST} as ${SERVER_USER}...${NC}"

# Deploy via SSH
ssh -o ConnectTimeout=10 "${SERVER_USER}@${SERVER_HOST}" << 'EOFSERVER'
    set -euo pipefail
    
    PROJECT_PATH="/home/deployer/goexplorer"
    
    echo "📁 Changing to project directory..."
    cd "$PROJECT_PATH"
    
    echo "📥 Pulling latest code from GitHub..."
    git pull origin main
    
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate || source /opt/goexplorer-venv/bin/activate
    
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt --quiet
    
    echo "🗄️  Running Django system checks..."
    python manage.py check
    
    echo "🔄 Running migrations..."
    python manage.py migrate --noinput
    
    echo "📂 Collecting static files..."
    python manage.py collectstatic --noinput
    
    echo "🔧 Installing systemd service..."
    sudo cp deploy/gunicorn.goexplorer.service /etc/systemd/system/gunicorn-goexplorer.service
    sudo systemctl daemon-reload
    
    echo "🔧 Installing Nginx configuration..."
    sudo cp deploy/nginx.goexplorer.dev.conf /etc/nginx/sites-available/goexplorer-dev
    sudo ln -sf /etc/nginx/sites-available/goexplorer-dev /etc/nginx/sites-enabled/goexplorer-dev
    
    echo "✓ Validating Nginx configuration..."
    sudo nginx -t
    
    echo "🛑 Stopping Gunicorn service..."
    sudo systemctl stop gunicorn-goexplorer || true
    
    echo "🧹 Cleaning old socket..."
    sudo rm -f /run/gunicorn-goexplorer.sock /run/gunicorn-goexplorer/goexplorer.sock || true
    
    echo "🚀 Starting Gunicorn service..."
    sudo systemctl start gunicorn-goexplorer
    sudo systemctl enable gunicorn-goexplorer
    
    echo "⏳ Waiting for socket to be created..."
    for i in {1..10}; do
        if [ -S /run/gunicorn-goexplorer/goexplorer.sock ]; then
            echo "✓ Socket created successfully"
            break
        fi
        echo "  Waiting... ($i/10)"
        sleep 1
    done
    
    if [ ! -S /run/gunicorn-goexplorer/goexplorer.sock ]; then
        echo "✗ ERROR: Socket not created! Checking logs..."
        journalctl -u gunicorn-goexplorer -n 20
        exit 1
    fi
    
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "📊 SERVICE STATUS:"
    echo "─────────────────────────────────────"
    echo "Gunicorn:"
    sudo systemctl status gunicorn-goexplorer --no-pager | head -7
    echo ""
    echo "Nginx:"
    sudo systemctl status nginx --no-pager | head -7
    echo ""
    echo "Socket:"
    ls -la /run/gunicorn-goexplorer/goexplorer.sock 2>/dev/null || echo "⚠️  Socket not found"
    echo ""
    echo "Recent Gunicorn logs:"
    journalctl -u gunicorn-goexplorer -n 10 --no-pager | tail -5
    
EOFSERVER

echo -e "${GREEN}✓ Server deployment complete${NC}"

# ============================================================================
# SECTION 4: VALIDATION
# ============================================================================
echo -e "\n${YELLOW}[VALIDATION] Testing application...${NC}"

# Wait for services to stabilize
sleep 2

# Test HTTP response
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://goexplorer-dev.cloud/ 2>/dev/null || echo "000")

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "301" ]; then
    echo -e "${GREEN}✓ Application responding with HTTP $RESPONSE${NC}"
elif [ "$RESPONSE" = "502" ]; then
    echo -e "${RED}✗ Still getting 502! Check logs:${NC}"
    echo "  ssh deployer@goexplorer-dev.cloud"
    echo "  journalctl -u gunicorn-goexplorer -n 50"
    exit 1
else
    echo -e "${YELLOW}⚠️  Unexpected response code: $RESPONSE${NC}"
fi

# ============================================================================
# SECTION 5: SUCCESS
# ============================================================================
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✓ DEPLOYMENT SUCCESSFUL!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}🌐 Access Points:${NC}"
echo "  Web:    http://goexplorer-dev.cloud"
echo "  Admin:  http://goexplorer-dev.cloud/admin"
echo ""

echo -e "${BLUE}🔍 Monitoring:${NC}"
echo "  View logs: ssh deployer@goexplorer-dev.cloud 'journalctl -u gunicorn-goexplorer -f'"
echo "  Status:    ssh deployer@goexplorer-dev.cloud 'sudo systemctl status gunicorn-goexplorer nginx'"
echo ""

echo -e "${BLUE}🐛 Troubleshooting:${NC}"
echo "  Gunicorn logs: journalctl -u gunicorn-goexplorer -n 50"
echo "  Nginx logs:    tail -f /var/log/nginx/error.log"
echo "  Django logs:   tail -f /home/deployer/goexplorer/logs/django.log"
echo ""
