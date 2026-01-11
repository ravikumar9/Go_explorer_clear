# PRODUCTION VERIFICATION CHECKLIST

## 🚀 Server-Side Execution

Copy the script to your server and run:

```bash
scp fix_static_production.sh deployer@goexplorer-dev.cloud:~/
ssh deployer@goexplorer-dev.cloud

cd ~/Go_explorer_clear
chmod +x fix_static_production.sh
./fix_static_production.sh
```

All output should show ✓ checkmarks. If any ❌ appears, stop and troubleshoot.

---

## ✅ Post-Fix Verification (Browser)

### 1. Django Admin Static Files (MUST PASS)

Open incognito: `http://goexplorer-dev.cloud/admin/`

**Visual Checks:**
- [ ] Page is **fully styled** (blue header bar visible)
- [ ] Login form is **centered** with proper styling
- [ ] Form inputs have borders and styling
- [ ] Submit button is styled

**Console Checks (F12):**
- [ ] Click F12 to open Developer Tools
- [ ] Go to **Console** tab
- [ ] Look for **404 errors** - there should be **ZERO**
- [ ] Check **Network** tab:
  - [ ] `/static/admin/css/base.css` → **200 OK**
  - [ ] `/static/admin/css/login.css` → **200 OK**
  - [ ] `/static/admin/js/theme.js` → **200 OK**

**Screenshot 1 Required:** Full admin login page + console showing zero 404s

---

### 2. Application Static Files

Navigate to: `http://goexplorer-dev.cloud/hotels/`

**Visual Checks:**
- [ ] Hotel list loads
- [ ] Hotel filter section visible (property type, amenities dropdowns)
- [ ] Images render (or show placeholder SVG)
- [ ] Price widget shows numbers (not NaN)

**Console Checks:**
- [ ] Open F12 Console
- [ ] Check for any 404 errors - should be **ZERO**
- [ ] Network tab should show:
  - [ ] `/static/css/booking-styles.css` → **200 OK**
  - [ ] `/static/js/booking-utilities.js` → **200 OK**
  - [ ] `/static/images/hotel_placeholder.svg` → **200 OK**

**Screenshot 2 Required:** Hotel list page showing filters + console with zero 404s

---

### 3. Media Files (Images)

Still on hotels page:

**Visual Checks:**
- [ ] Hotel images visible (either real images or placeholder)
- [ ] Package images visible (if you navigate to `/packages/`)
- [ ] No broken image icons

**Console Checks:**
- [ ] Network tab should show `/media/` URLs returning **200 OK**
- [ ] No `/media/` 404 errors

---

### 4. Wallet & Cashback Display

Navigate to: `http://goexplorer-dev.cloud/users/login/`

**Login as testuser:**
- Username: `testuser`
- Password: `testpass123`

Then navigate to a hotel and attempt to book:

**Visual Checks:**
- [ ] Payment page loads
- [ ] **Wallet section visible** showing "₹5,000" balance
- [ ] **Cashback section visible** showing "₹1,000" with expiry date
- [ ] Payment method options visible (Wallet, Razorpay, etc.)

**Screenshot 3 Required:** Payment page showing wallet balance + cashback

---

### 5. Hotel Filters Functionality

Navigate to: `http://goexplorer-dev.cloud/hotels/`

**Visual Checks:**
- [ ] Property Type filter visible with options (Hotel, Resort, Villa, etc.)
- [ ] Amenities filter visible with checkboxes (WiFi, Parking, Pool, etc.)
- [ ] Star Rating filter visible
- [ ] Price range slider visible
- [ ] All filters are **styled** (CSS loaded)

**Functional Checks:**
- [ ] Select a property type filter
- [ ] Click "Search Hotels"
- [ ] Results update correctly
- [ ] Navigate back using browser back button
- [ ] Filters **persist** (show previous selections)

**No NaN Check:**
- [ ] Click on a hotel detail
- [ ] Look at price widget
- [ ] "Base:", "GST:", "Total:" should all show **numbers**
- [ ] None should show **NaN**

---

### 6. Final Console Check

On any page, press F12 and check **Console** tab:

**Must See:**
- ✅ Zero 404 errors
- ✅ Zero JavaScript errors
- ✅ Benign warnings OK:
  - `pkg_resources deprecation` (from razorpay) → OK
  - `DEFAULT_PAGINATION_CLASS` (from DRF) → OK

**Must NOT See:**
- ❌ `/static/` 404 errors
- ❌ `/media/` 404 errors
- ❌ JavaScript syntax errors
- ❌ CSRF errors

**Screenshot 4 Required:** Browser console showing zero 404/error messages

---

## 📸 REQUIRED SCREENSHOTS (Attach All 4)

### Screenshot 1: Admin Login (Styled)
- Show admin login page with full styling
- Include console tab showing zero 404s

### Screenshot 2: Hotel List (Filters + Images)
- Show hotel filter section (property type, amenities, star rating)
- Show hotel cards with images
- Include console showing zero 404s for `/static/` and `/media/` URLs

### Screenshot 3: Payment Page (Wallet + Cashback)
- Show logged-in payment page
- Clearly visible: "Wallet Balance: ₹5,000"
- Clearly visible: "Available Cashback: ₹1,000" with expiry date
- Show payment method options

### Screenshot 4: Console - Zero Errors
- Full browser console view
- Zero 404 errors
- Zero JavaScript errors
- Show network tab with `/static/` requests returning 200 OK

---

## 🔧 Troubleshooting If Still Broken

If admin is still unstyled after running the script, execute on server:

```bash
# Check nginx error log
sudo tail -50 /var/log/nginx/error.log

# Check if files actually exist
ls -lh /home/deployer/Go_explorer_clear/staticfiles/admin/css/base.css

# Check permissions
sudo -u www-data test -r /home/deployer/Go_explorer_clear/staticfiles/admin/css/base.css && echo "OK" || echo "PERMISSION DENIED"

# Test direct nginx access
curl -I http://localhost/static/admin/css/base.css

# Check gunicorn
sudo systemctl status gunicorn

# Check if gunicorn is actually running on port 8000
netstat -tln | grep 8000
```

Post any error messages here.

---

## ✅ Acceptance Criteria (ALL MUST PASS)

- [ ] Admin login page fully styled
- [ ] Zero static 404 errors in console
- [ ] Hotel filters visible and functional
- [ ] Images loading (no 404s)
- [ ] Wallet balance visible (₹5,000)
- [ ] Cashback visible with expiry (₹1,000)
- [ ] No NaN in price widget
- [ ] Hotel filters persist after search
- [ ] All 4 screenshots attached and clear

**Only after ALL above pass** → Report: **"SERVER VERIFIED – READY FOR REVIEW"**
