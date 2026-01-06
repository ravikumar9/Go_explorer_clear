#!/bin/bash
# Comprehensive server diagnostic and fix script
# This will be run ON the server to diagnose and fix the populate() reentrant issue

set -e

cd ~/Go_explorer_clear
source venv/bin/activate

echo "========================================"
echo "Server Diagnostic & Fix Report"
echo "========================================"
echo ""

echo "[1] Python & Django Versions"
echo "Python: $(python --version)"
echo "Django: $(python -c 'import django; print(django.VERSION)')"
echo ""

echo "[2] Clearing all Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✓ Cache cleared"
echo ""

echo "[3] Checking populate_bookings.py structure..."
echo "First 15 lines of populate_bookings.py:"
head -15 populate_bookings.py
echo ""
echo "Last 10 lines of populate_bookings.py:"
tail -10 populate_bookings.py
echo ""

echo "[4] Checking for any django.setup() calls in app code..."
echo "Searching for problematic django.setup() calls (excluding venv)..."
grep -r "django.setup()" --include="*.py" . 2>/dev/null | grep -v ".venv" | grep -v "__pycache__" || echo "None found (good!)"
echo ""

echo "[5] Testing manage.py check (this is the failing command)..."
echo "Running: python manage.py check"
if python manage.py check 2>&1 | head -50; then
    echo ""
    echo "✅ manage.py check PASSED!"
else
    echo ""
    echo "❌ manage.py check FAILED - See errors above"
fi
echo ""

echo "[6] If check passed, attempt migrations..."
if python manage.py migrate --noinput 2>&1 | tail -20; then
    echo "✅ Migrations successful"
else
    echo "❌ Migrations failed"
fi

echo ""
echo "========================================"
echo "Report Complete"
echo "========================================"
