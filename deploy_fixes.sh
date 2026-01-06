#!/bin/bash

# ============================================================================
# GOEXPLORER DEPLOYMENT SCRIPT
# Deploy E2E Booking Flow Fixes to Production Server
# Usage: ./deploy_fixes.sh
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_HOST="goexplorer-dev.cloud"
SERVER_USER="deployer"
SERVER_PASSWORD="Thepowerof@9"
PROJECT_PATH="/home/deployer/goexplorer"  # Adjust if different
BRANCH="main"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GoExplorer E2E Booking Flow - Deployment Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Local validation
echo -e "\n${YELLOW}[1/6] Validating local changes...${NC}"
if [ ! -f "manage.py" ]; then
    echo -e "${RED}✗ ERROR: manage.py not found. Run from project root!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Project structure valid${NC}"

# Step 2: Git operations
echo -e "\n${YELLOW}[2/6] Committing local changes...${NC}"
git add -A
git commit -m "Fix: E2E booking flow - calendar dates, payment integration, image loading" || true
git push origin $BRANCH
echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"

# Step 3: Server deployment
echo -e "\n${YELLOW}[3/6] Pulling code on server...${NC}"
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
    cd /home/deployer/goexplorer
    git pull origin main
    echo "✓ Code pulled successfully"
EOF

# Step 4: Install dependencies
echo -e "\n${YELLOW}[4/6] Installing dependencies on server...${NC}"
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
    source venv/bin/activate 2>/dev/null || source /opt/goexplorer-venv/bin/activate
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
EOF

# Step 5: Database & Static files
echo -e "\n${YELLOW}[5/6] Running migrations and collecting static files...${NC}"
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
    cd /home/deployer/goexplorer
    source venv/bin/activate 2>/dev/null || source /opt/goexplorer-venv/bin/activate
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    echo "✓ Migrations and static files updated"
EOF

# Step 6: Restart services
echo -e "\n${YELLOW}[6/6] Restarting application services...${NC}"
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
    sudo systemctl restart goexplorer gunicorn nginx
    echo "✓ Services restarted"
    echo ""
    echo "Service Status:"
    sudo systemctl status goexplorer --no-pager | head -5
    sudo systemctl status gunicorn --no-pager | head -5
    sudo systemctl status nginx --no-pager | head -5
EOF

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✓ DEPLOYMENT COMPLETE!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Test in browser: http://goexplorer-dev.cloud/hotels/"
echo "2. Test booking flow end-to-end"
echo "3. Check browser console (F12) for any errors"
echo "4. Verify payment integration works"
echo ""
echo -e "${YELLOW}To check server logs:${NC}"
echo "  ssh deployer@goexplorer-dev.cloud"
echo "  tail -f /var/log/goexplorer/error.log"
echo ""

