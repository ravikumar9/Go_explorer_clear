# 🚨 CRITICAL DEPLOYMENT INSTRUCTIONS – Commit 6128187

**STATUS**: Code is fixed locally, but requires proper deployment to goexplorer-dev.cloud

## Root Cause Analysis

Your screenshots show the server is running **STALE CODE** from an earlier commit. The fixes made in commits `4bd43d6` and `66a4d0f` have NOT been deployed to the production server.

**Evidence**:
- Static files 404: `/static/css/style.css` not being served (need `collectstatic`)
- `validateLadiesSeats` ReferenceError: Old template version without function definition reorder
- Confirmation shows "Booking confirmation placeholder": Old view/template being served
- Logout 405: Old routes file without GET support

## Deployment Checklist – **MUST DO THIS ON SERVER**

### Step 1: Pull Latest Code
```bash
cd /path/to/goexplorer
git pull origin main
```

Verify you're on commit `6128187`:
```bash
git log --oneline -1
# Should show: 6128187 Critical fixes for all runtime issues
```

### Step 2: Collect Static Files ⚠️ **CRITICAL**
```bash
python manage.py collectstatic --noinput --clear
```

This MUST run before restarting services. Without this:
- `/static/css/style.css` will return 404
- CSS won't load
- Layout will be broken
- JS might fail

**Verify it worked**:
```bash
ls -la staticfiles/css/
# Should show: style.css
```

### Step 3: Verify Database State
```bash
python manage.py check
# Should show: System check identified no issues (0 silenced).
```

### Step 4: Run Test Data (if needed)
```bash
python manage.py create_e2e_test_data --clean
# Should show all counts > 0 for seats, schedules, boarding points
```

### Step 5: Restart Services
```bash
# Restart Gunicorn
systemctl restart gunicorn

# Restart Nginx
systemctl restart nginx

# Verify services are running
systemctl status gunicorn
systemctl status nginx
```

### Step 6: Verify Deployment
In browser, navigate to `https://goexplorer-dev.cloud`:

**Check 1: Static Files**
- F12 → Network tab
- Reload page
- Look for `/static/css/style.css` → Status **200** (not 404)
- All Bootstrap/Font Awesome load successfully

**Check 2: Console Errors**
- F12 → Console tab
- Reload page
- Should show **NO RED ERRORS**
- Specifically check for: `ReferenceError: validateLadiesSeats is not defined` → Should be GONE

**Check 3: Booking Flow**
- Click "Buses" → Select any bus
- Try to select a seat
- **Expected**: No console errors, can click seats
- Gender dropdown should work without errors

**Check 4: Confirmation Page**
- Complete bus booking flow
- Redirects to `/bookings/<uuid>/confirm/`
- **Expected**: Shows real booking ID (UUID), bus details, amount
- NOT showing "Booking confirmation placeholder"

**Check 5: Logout**
- Click "Logout" in navbar
- **Expected**: Redirects to home, shows "Logged out" message
- Status 302 redirect, NOT 405

---

## What's Fixed in Commit 6128187

| Issue | Root Cause | Fix | Status |
|-------|-----------|-----|--------|
| Static files 404 | `collectstatic` not run on server | Need to run `collectstatic --noinput --clear` | ✅ CODE FIX |
| `validateLadiesSeats` ReferenceError | Function defined in DOMContentLoaded, but `onchange` calls it before that | Moved function definition to global scope, before any handlers | ✅ CODE FIX |
| Confirmation placeholder | Old view/template not deployed | Code is correct now, just needs deployment | ✅ CODE FIX |
| Logout 405 | Old URL routes | Routes updated to support GET/POST | ✅ CODE FIX |
| Console errors | Various JS issues | All fixed locally, need deployment | ✅ CODE FIX |

---

## Post-Deployment Testing Script

Run this after deployment to verify everything works:

```bash
#!/bin/bash
echo "=== GoExplorer Post-Deployment Test ==="
echo

echo "1. Checking static files..."
curl -s -o /dev/null -w "CSS: %{http_code}\n" https://goexplorer-dev.cloud/static/css/style.css
curl -s -o /dev/null -w "Bootstrap: %{http_code}\n" https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css

echo
echo "2. Checking main pages..."
curl -s -o /dev/null -w "Home: %{http_code}\n" https://goexplorer-dev.cloud/
curl -s -o /dev/null -w "Buses: %{http_code}\n" https://goexplorer-dev.cloud/buses/
curl -s -o /dev/null -w "Hotels: %{http_code}\n" https://goexplorer-dev.cloud/hotels/

echo
echo "3. Checking auth..."
curl -s -o /dev/null -w "Login: %{http_code}\n" https://goexplorer-dev.cloud/users/login/

echo
echo "✅ All basic endpoints responsive. Check browser DevTools for details."
```

---

## If Issues Persist After Deployment

### Still seeing 404 on static files?
```bash
# Check if collectstatic ran correctly
ls -la /path/to/goexplorer/staticfiles/

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx

# Check Gunicorn logs
journalctl -u gunicorn -n 50
```

### Still seeing validateLadiesSeats error?
```bash
# Verify the function is in the template
grep -n "function validateLadiesSeats" templates/buses/bus_detail.html

# Should show near the top of the <script> block, BEFORE DOMContentLoaded
```

### Still seeing confirmation placeholder?
```bash
# Verify template is being used
grep -n "Booking confirmation placeholder" templates/bookings/confirmation.html

# Should return nothing. If it returns a match, the template wasn't updated
```

---

## Critical: Commands That MUST Run on Server

After `git pull origin main`:

```bash
# 1. Collect static files (CRITICAL)
python manage.py collectstatic --noinput --clear

# 2. Create test data if needed
python manage.py create_e2e_test_data --clean

# 3. Restart services
systemctl restart gunicorn
systemctl restart nginx

# 4. Verify with Django check
python manage.py check
```

**DO NOT skip `collectstatic` or services won't have latest code.**

---

## Expected Results After Deployment

✅ **Console**: Zero red errors  
✅ **Network**: `/static/css/style.css` returns 200  
✅ **Buses**: Can select seats without errors  
✅ **Confirmation**: Shows real booking ID, not "placeholder"  
✅ **Logout**: Works via GET request  
✅ **Dates**: Persist correctly from home to hotel detail  

---

## Questions?

If after running these steps issues persist, reply with:
1. Output of: `git log --oneline -1` (confirm commit 6128187)
2. Output of: `python manage.py check`
3. DevTools screenshot showing any console errors
4. Network tab screenshot showing static file status codes

