#!/bin/bash
# ============================================================================
# EMERGENCY 502 FIX - QUICK DIAGNOSTICS & RESTART
# Run this on the server: bash fix_502.sh
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          EMERGENCY 502 BAD GATEWAY DIAGNOSTIC               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

PROJECT_PATH="/home/deployer/goexplorer"

# ============================================================================
# 1. DIAGNOSE THE PROBLEM
# ============================================================================
echo -e "\n${YELLOW}[1] GUNICORN STATUS${NC}"
echo "─────────────────────────────────────"

if systemctl is-active --quiet gunicorn-goexplorer; then
    echo -e "${GREEN}✓ Gunicorn service is RUNNING${NC}"
    systemctl status gunicorn-goexplorer --no-pager | head -5
else
    echo -e "${RED}✗ Gunicorn service is STOPPED${NC}"
    echo "  Will restart in step [4]"
fi

echo ""
echo -e "${YELLOW}[2] SOCKET STATUS${NC}"
echo "─────────────────────────────────────"

SOCKET_PATH="/run/gunicorn-goexplorer/goexplorer.sock"

if [ -S "$SOCKET_PATH" ]; then
    echo -e "${GREEN}✓ Socket EXISTS at $SOCKET_PATH${NC}"
    ls -la "$SOCKET_PATH"
    
    # Test socket connectivity
    if timeout 2 bash -c "echo '' | socat - UNIX-CONNECT:$SOCKET_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓ Socket is ACCESSIBLE${NC}"
    else
        echo -e "${RED}✗ Socket is NOT accessible${NC}"
    fi
else
    echo -e "${RED}✗ Socket DOES NOT EXIST at $SOCKET_PATH${NC}"
    echo "  Expected: Gunicorn will create it on startup"
fi

echo ""
echo -e "${YELLOW}[3] NGINX STATUS${NC}"
echo "─────────────────────────────────────"

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx service is RUNNING${NC}"
    systemctl status nginx --no-pager | head -3
else
    echo -e "${RED}✗ Nginx service is STOPPED${NC}"
fi

# Validate Nginx config
echo "  Validating configuration..."
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Nginx config is valid${NC}"
else
    echo -e "${RED}✗ Nginx config has errors${NC}"
    sudo nginx -t
fi

echo ""
echo -e "${YELLOW}[4] RECENT ERRORS${NC}"
echo "─────────────────────────────────────"

echo "Gunicorn errors:"
journalctl -u gunicorn-goexplorer -n 5 --no-pager 2>/dev/null | grep -i error || echo "  No errors found"

echo ""
echo "Nginx errors:"
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "  Cannot read nginx logs"

# ============================================================================
# 5. FIX PROCEDURE
# ============================================================================
echo -e "\n${YELLOW}[5] APPLYING FIX${NC}"
echo "─────────────────────────────────────"

echo "🛑 Step 1: Stopping Gunicorn..."
sudo systemctl stop gunicorn-goexplorer || true
sleep 1

echo "🧹 Step 2: Cleaning old socket..."
sudo rm -f /run/gunicorn-goexplorer.sock /run/gunicorn-goexplorer/goexplorer.sock 2>/dev/null || true
sudo rm -rf /run/gunicorn-goexplorer 2>/dev/null || true

echo "🚀 Step 3: Starting Gunicorn..."
sudo systemctl start gunicorn-goexplorer

echo "⏳ Step 4: Waiting for socket..."
for i in {1..15}; do
    if [ -S "$SOCKET_PATH" ]; then
        echo -e "${GREEN}✓ Socket created in ${i}s${NC}"
        ls -la "$SOCKET_PATH"
        break
    fi
    echo "  Attempt $i/15..."
    sleep 1
done

if [ ! -S "$SOCKET_PATH" ]; then
    echo -e "${RED}✗ Socket failed to create after 15s${NC}"
    echo "  Checking Gunicorn logs..."
    journalctl -u gunicorn-goexplorer -n 50
    exit 1
fi

echo "🔄 Step 5: Reloading Nginx..."
sudo systemctl reload nginx

sleep 2

echo -e "${GREEN}✓ Fix applied${NC}"

# ============================================================================
# 6. VERIFY FIX
# ============================================================================
echo -e "\n${YELLOW}[6] VERIFICATION${NC}"
echo "─────────────────────────────────────"

# Test localhost
echo "Testing: curl http://localhost:8000/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "301" ] || [ "$RESPONSE" = "302" ]; then
    echo -e "${GREEN}✓ Localhost responds with HTTP $RESPONSE${NC}"
else
    echo -e "${RED}✗ Localhost responds with HTTP $RESPONSE${NC}"
fi

# Test via hostname (if possible)
echo "Testing: curl http://goexplorer-dev.cloud/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://goexplorer-dev.cloud/ 2>/dev/null || echo "000")

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "301" ] || [ "$RESPONSE" = "302" ]; then
    echo -e "${GREEN}✓ Domain responds with HTTP $RESPONSE${NC}"
elif [ "$RESPONSE" = "502" ]; then
    echo -e "${RED}✗ Still getting 502!${NC}"
    echo ""
    echo "  Try these steps manually:"
    echo "  1. Check permissions: ls -la /run/gunicorn-goexplorer/"
    echo "  2. Check Gunicorn PID: ps aux | grep gunicorn"
    echo "  3. View Gunicorn logs: journalctl -u gunicorn-goexplorer -f"
    echo "  4. Check Django checks: cd $PROJECT_PATH && python manage.py check"
    exit 1
else
    echo -e "${YELLOW}⚠️  Unexpected response: $RESPONSE${NC}"
fi

# ============================================================================
# 7. SUCCESS
# ============================================================================
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✓ 502 FIX COMPLETE - SERVICE RESTORED             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo ""
echo "Final Status:"
echo "─────────────────────────────────────"
systemctl status gunicorn-goexplorer --no-pager | head -4
echo ""
systemctl status nginx --no-pager | head -4

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test application: http://goexplorer-dev.cloud"
echo "2. Monitor logs: journalctl -u gunicorn-goexplorer -f"
echo "3. If issues persist, run with more details: journalctl -u gunicorn-goexplorer -n 100"
