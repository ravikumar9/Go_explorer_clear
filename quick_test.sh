#!/bin/bash

# ============================================================================
# QUICK TEST - Verify fixes work locally before deployment
# Run: bash quick_test.sh
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         GoExplorer E2E Booking - Quick Local Test         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ ERROR: Not in GoExplorer project directory!"
    echo "   Please run from: /workspaces/Go_explorer_clear"
    exit 1
fi

echo "✓ Project directory verified"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version
echo ""

# Check Django installation
echo "[2/5] Checking Django installation..."
python3 -c "import django; print(f'Django {django.get_version()} installed')" || {
    echo "❌ Django not installed. Run: pip3 install -r requirements.txt"
    exit 1
}
echo ""

# Check database
echo "[3/5] Checking database..."
python3 manage.py migrate --noinput > /dev/null 2>&1
echo "✓ Database migrations applied"
echo ""

# Run E2E tests
echo "[4/5] Running E2E tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 test_e2e_complete.py
TEST_RESULT=$?
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
echo "[5/5] Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "Next steps:"
    echo "  1. Test in browser: python3 manage.py runserver"
    echo "  2. Open: http://localhost:8000/hotels/"
    echo "  3. Test booking flow manually"
    echo "  4. Deploy: ./deploy_fixes.sh"
else
    echo "❌ Some tests FAILED"
    echo ""
    echo "Review the errors above and:"
    echo "  1. Check browser console: http://localhost:8000/hotels/"
    echo "  2. Check database: python3 manage.py dbshell"
    echo "  3. Check logs: cat logs/*.log"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

exit $TEST_RESULT
