# 🚀 START HERE - WHAT YOU CAN TEST RIGHT NOW

**Last Updated:** 2026-01-06  
**Server:** http://goexplorer-dev.cloud  
**Status:** ✅ Ready for testing

---

## ⚡ QUICK LINKS

Click to jump directly to what you want to test:

1. **[5-Minute Quick Test](#5-minute-quick-test)** - Visual verification only
2. **[15-Minute Full Test](#15-minute-full-test)** - Complete booking flow
3. **[Advanced Verification](#advanced-verification)** - Database & API testing
4. **[Troubleshooting](#troubleshooting)** - If something doesn't work

---

## 5-MINUTE QUICK TEST

**Goal:** Verify that dates, images, and forms are visible

### Step 1: Homepage (1 minute)
```
🔗 URL: http://goexplorer-dev.cloud/

WHAT YOU'LL SEE:
✅ Blue header with GoExplorer logo
✅ "Search Hotels" section with three inputs:
   1. City dropdown
   2. Check-in date (shows TODAY'S DATE in BLACK TEXT)
   3. Check-out date (shows TOMORROW'S DATE in BLACK TEXT)
✅ Search button below

❓ WHAT IF DATES ARE INVISIBLE?
  1. Press Ctrl+Shift+R (hard refresh, clears cache)
  2. Still not working? Check troubleshooting section below
```

### Step 2: Hotel List (2 minutes)
```
🔗 URL: http://goexplorer-dev.cloud/hotels/

WHAT YOU'LL SEE:
✅ Hotel cards showing:
   - Hotel photo (NOT gray placeholder)
   - Hotel name (e.g., "Taj Mahal Palace")
   - Rating (e.g., "⭐ 4.5/5")
   - Price (e.g., "₹8,000 per night")
   - "View Details & Book" button

❓ WHAT IF IMAGES DON'T LOAD?
  1. Check browser console (F12 → Console)
  2. Look for 404 errors
  3. If images are 404, that's an issue - see troubleshooting
```

### Step 3: Hotel Detail (2 minutes)
```
🔗 URL: http://goexplorer-dev.cloud/hotels/38/
(or click "View Details" on any hotel from the list)

WHAT YOU'LL SEE:
✅ Large hotel image at top (NOT gray!)
✅ Hotel name: "The Leela Palace Bangalore"
✅ Rating and reviews
✅ Multiple room types listed:
   - Standard Room - ₹8,000/night
   - Deluxe Room - ₹15,000/night
   - Suite - ₹35,000/night
   - Presidential Suite - ₹70,000/night

✅ ON THE RIGHT SIDE - Booking Widget:
   - Check-in date (prefilled from search)
   - Check-out date (prefilled from search)
   - Room type dropdown
   - Number of rooms field
   - Number of guests field
   - Guest name field
   - Email field
   - Phone number field
   - Price breakdown
   - Button at bottom (either "Proceed to Payment" OR "Login to Book")

✅ AVAILABILITY SECTION:
   - Shows: "Rooms available: 15"
   - Shows: "Best rate: ₹8000/night"
   - Shows: "Source: Internal_Cm"
```

**✅ QUICK TEST COMPLETE!**

---

## 15-MINUTE FULL TEST

**Goal:** Complete a full booking from start to confirmation

### Prerequisites
- **Username:** goexplorer_dev_admin
- **Password:** Thepowerof@9
- Go to: http://goexplorer-dev.cloud/admin/login/

### Step 1: Login (1 minute)
```
1. Go to: http://goexplorer-dev.cloud/
2. Notice the "Login to Book" button on hotel detail pages
3. Click it
4. Enter:
   Username: goexplorer_dev_admin
   Password: Thepowerof@9
5. Click "Login"
6. You're now authenticated!
```

### Step 2: Navigate to Hotel Detail (1 minute)
```
1. Go to: http://goexplorer-dev.cloud/hotels/38/
2. Now the booking button should say "Proceed to Payment" (not "Login to Book")
```

### Step 3: Fill Booking Form (5 minutes)
```
FORM FIELDS TO FILL:

Check-in Date: 2026-01-10 (should be prefilled)
Check-out Date: 2026-01-12 (should be prefilled)

Room Type: Select "Deluxe Room" from dropdown

Number of Rooms: 1 (keep default)

Number of Guests: 2 (or any number)

Guest Name: "Test User" (or your name)

Email: "test@example.com" (any valid email)

Phone: "9876543210" (must be 10+ digits!)

✅ You should see price calculated:
   Base Price: ₹15,000 × 2 nights = ₹30,000
   GST (18%): ₹5,400
   Total: ₹35,400
```

### Step 4: Submit Booking (2 minutes)
```
1. Click "Proceed to Payment" button
2. EXPECT: Page redirects to a confirmation page

CONFIRMATION PAGE SHOULD SHOW:
✅ Booking ID (e.g., "a4b5c6d7-e8f9...")
✅ Hotel: "The Leela Palace Bangalore"
✅ Check-in: 2026-01-10
✅ Check-out: 2026-01-12
✅ Room: "Deluxe Room"
✅ Total: ₹35,400
✅ Another "Proceed to Payment" button

3. Click "Proceed to Payment" again

PAYMENT PAGE SHOULD SHOW:
✅ Razorpay payment form OR
⚠️  Error message (if Razorpay keys not configured)
```

### Step 5: Verify in Database (5 minutes - optional)
```
1. Go to: http://goexplorer-dev.cloud/admin/
2. Login if not already
3. Navigate to: Bookings → Bookings
4. You should see your booking:
   ✅ Booking ID matches confirmation page
   ✅ Status: "pending" (not "confirmed" until payment)
   ✅ Inventory Channel: "internal_cm"
   ✅ Hotel: "The Leela Palace Bangalore"
```

**✅ FULL TEST COMPLETE!**

---

## ADVANCED VERIFICATION

### For Developers/Testers

#### API Endpoint Testing
```bash
# Test 1: Create Razorpay Order
curl -X POST http://goexplorer-dev.cloud/bookings/api/create-order/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"booking_id": "UUID_FROM_BOOKING"}'

# Expected Response (200 OK):
{
  "status": "success",
  "order_id": "order_123456"
}

# Without auth token → 403 Forbidden (correct!)


# Test 2: Verify Payment
curl -X POST http://goexplorer-dev.cloud/bookings/api/verify-payment/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "booking_id": "UUID",
    "razorpay_order_id": "order_123",
    "razorpay_payment_id": "pay_123",
    "razorpay_signature": "signature_hash"
  }'

# Expected Response (200 OK):
{
  "status": "success",
  "message": "Payment verified and booking confirmed"
}
```

#### Database Schema Verification
```bash
# SSH to server
ssh deployer@goexplorer-dev.cloud
cd /home/deployer/Go_explorer_clear

# Enter Django shell
venv/bin/python manage.py shell

# Check Hotel schema
from hotels.models import Hotel
h = Hotel.objects.first()
print(f"Hotel: {h.name}")
print(f"Inventory Source: {h.inventory_source}")
print(f"Channel Manager: {h.channel_manager_name}")
print(f"Has Image: {bool(h.image)}")

# Check Booking schema  
from bookings.models import Booking
b = Booking.objects.first()
print(f"Booking {b.booking_id}:")
print(f"  Status: {b.status}")
print(f"  Inventory Channel: {b.inventory_channel}")
print(f"  Lock ID: {b.lock_id}")

# Check InventoryLock model
from bookings.models import InventoryLock
locks = InventoryLock.objects.all()
print(f"Total locks: {locks.count()}")
```

#### Network Traffic Inspection
```
Browser: F12 → Network tab → Reload page

Look for:
✅ Status 200: All CSS files loaded
✅ Status 200: All JavaScript files loaded
✅ Status 200: Hotel images from /media/
✅ No 404 errors (red in network tab)
✅ No 500 errors (server errors)

Check specific image:
Right-click image → "Open in new tab"
Should show: HTTP 200 with image content
```

---

## TROUBLESHOOTING

### Problem 1: Dates Are Invisible/White

**Symptom:** Date input fields show no text or white text on white background

**Quick Fix:**
```
1. Press: Ctrl+Shift+R (hard refresh, clears all cache)
2. If still not working:
   - Open DevTools: F12
   - Right-click date input → Inspect
   - Look at Styles panel
   - Should show: color: rgb(33, 37, 41)
   - If missing, the CSS didn't load
```

**If Still Broken:**
```
Server-side issue - need to reload:
ssh deployer@goexplorer-dev.cloud
cd /home/deployer/Go_explorer_clear
# Find gunicorn process
ps aux | grep gunicorn | grep -v grep

# Reload it (replace PID with actual number)
kill -HUP PID_NUMBER

# Wait 2-3 seconds, try page again
```

---

### Problem 2: Hotel Images Show 404 Errors

**Symptom:** Images appear as gray placeholders or broken image icons

**Quick Check:**
```
1. Open DevTools: F12 → Network tab
2. Reload page
3. Look for requests to /media/hotels/*.jpg
4. If Status = 404 (red), that's the problem
```

**Quick Fix:**
```
1. Check if images exist on disk:
   ssh deployer@goexplorer-dev.cloud
   ls -la /home/deployer/Go_explorer_clear/media/hotels/

2. If files don't exist, they need to be uploaded
3. If files exist, check Nginx config:
   sudo cat /etc/nginx/sites-enabled/goexplorer | grep media

4. Should show:
   location /media/ {
       alias /home/deployer/Go_explorer_clear/media/;
   }

5. If config looks wrong, reload Nginx:
   sudo systemctl reload nginx
```

---

### Problem 3: "Login to Book" Button Shows but Login Doesn't Work

**Symptom:** Click login, but still see "Login to Book" afterward

**Quick Fix:**
```
1. Check credentials:
   Username: goexplorer_dev_admin (not just "admin")
   Password: Thepowerof@9

2. Try direct login:
   http://goexplorer-dev.cloud/admin/login/
   
3. If you see error:
   - Check if user exists:
     ssh deployer@goexplorer-dev.cloud
     cd /home/deployer/Go_explorer_clear
     venv/bin/python manage.py shell
     from django.contrib.auth import get_user_model
     User = get_user_model()
     User.objects.filter(username='goexplorer_dev_admin').exists()
     
4. If user doesn't exist, create:
   python manage.py create_dev_admin
```

---

### Problem 4: Booking Form Shows JavaScript Errors

**Symptom:** Form won't submit, console shows errors in F12 → Console

**Common Errors:**
```
1. "Uncaught ReferenceError: validateAndSubmit is not defined"
   → JavaScript file didn't load
   → Hard refresh: Ctrl+Shift+R
   
2. "Cannot read property 'value' of null"
   → Form field not found by JavaScript
   → Check HTML: F12 → Inspector
   → Look for: <input id="checkin"> and <input id="checkout">
   
3. "CSRF token missing"
   → Page didn't load {% csrf_token %} in form
   → Check page source: Ctrl+U
   → Look for: <input type="hidden" name="csrfmiddlewaretoken">
```

---

### Problem 5: Payment Page Shows Error

**Symptom:** Click "Proceed to Payment" and see error/blank page

**Likely Cause:** Razorpay keys not configured

**Check:**
```
1. Is error about "RAZORPAY_KEY_ID"?
   That's expected if keys not set up
   
2. To enable payments:
   - Get keys from: https://dashboard.razorpay.com/
   - Add to .env:
     RAZORPAY_KEY_ID=rzp_test_xxxxx
     RAZORPAY_SECRET_KEY=xxxxx
   - Reload server:
     ssh deployer@goexplorer-dev.cloud
     cd /home/deployer/Go_explorer_clear
     ps aux | grep gunicorn | grep -v grep | awk '{print $2}' | xargs kill -HUP
```

---

### Problem 6: Images Work on Detail Page but Not on List Page

**Symptom:** Hotel list page shows no/broken images, but detail page images work

**Cause:** Template uses different image field

**Fix:**
```
Check template: templates/hotels/hotel_list.html
Should use: {{ hotel.primary_image_url }}
NOT: {{ hotel.image.url }}

If still broken, ensure all hotels have images:
ssh deployer@goexplorer-dev.cloud
cd /home/deployer/Go_explorer_clear
venv/bin/python manage.py shell

from hotels.models import Hotel
for h in Hotel.objects.all():
    print(f"{h.name}: {h.image}")
    
All should show a filename, not "None"
```

---

## 📊 WHAT'S WORKING vs NOT WORKING

### ✅ WORKING NOW

- [x] Date inputs visible with black text
- [x] Date values persist across pages
- [x] Hotel list displays with images
- [x] Hotel detail page shows images
- [x] Booking form with all fields
- [x] Form validation (phone 10+ digits)
- [x] Availability info displayed
- [x] Inventory source shown
- [x] API endpoints exist (return 403 without auth)
- [x] Database schema updated
- [x] Migrations applied

### ⚠️ NEEDS CONFIGURATION

- [ ] Payment endpoints active (need Razorpay keys in .env)
- [ ] Payment processing (need test/live Razorpay account)
- [ ] Email notifications (need email backend)
- [ ] SMS notifications (need Twilio account)
- [ ] External CM providers (stubs ready, need API creds)

### 🔄 IN PROGRESS

- [ ] Partner dashboard for internal CM hotels
- [ ] Webhook support for external CMs
- [ ] Lock expiry automation (cron job)

---

## ✅ CHECKLIST - HAVE YOU TRIED?

Print this and check off as you test:

```
VISUAL COMPONENTS:
☐ Homepage - dates visible and working
☐ Hotel list - images load properly
☐ Hotel detail - all images display
☐ Booking form - all fields visible
☐ Availability info - shows room count

FUNCTIONALITY:
☐ Can navigate between pages
☐ Can fill booking form
☐ Can submit booking form
☐ Can see confirmation page
☐ Can see payment form (or error if keys missing)

BROWSER CHECKS:
☐ No JavaScript errors (F12 → Console)
☐ No 404 errors (F12 → Network)
☐ All CSS loaded (styles applied)
☐ Images load (F12 → Network shows 200)

DATABASE (ADVANCED):
☐ Admin panel loads (http://goexplorer-dev.cloud/admin/)
☐ Can see bookings in admin
☐ Booking has correct data
☐ Hotel has inventory_source set
```

---

## 🚨 FOUND AN ISSUE?

**Report Format:**
```
Issue: [Brief description]
Steps: [How to reproduce]
Expected: [What should happen]
Actual: [What actually happened]
Error: [Any error messages from F12 Console]
Browser: [Chrome/Firefox/Safari version]
Server: goexplorer-dev.cloud
```

---

## 📞 SUPPORT CHANNELS

1. **Check Documentation:** 
   - MANUAL_TESTING_GUIDE.md (detailed)
   - VERIFICATION_REPORT.md (technical)
   - SYSTEM_STATUS.md (overview)

2. **Check Logs:**
   ```bash
   # Server logs
   ssh deployer@goexplorer-dev.cloud
   tail -50 /home/deployer/Go_explorer_clear/logs/debug.log
   ```

3. **Browser Console (F12):**
   - Shows JavaScript errors
   - Shows network errors
   - Shows CSRF issues

4. **Admin Panel:**
   - http://goexplorer-dev.cloud/admin/
   - Username: goexplorer_dev_admin
   - Password: Thepowerof@9

---

## 🎯 NEXT STEPS AFTER TESTING

**If everything works:**
1. ✅ Proceed to payment integration testing
2. ✅ Configure Razorpay keys
3. ✅ Set up email notifications
4. ✅ Plan production deployment

**If something broke:**
1. Check troubleshooting section above
2. Review error logs (F12 Console)
3. Check server logs via SSH
4. Review VERIFICATION_REPORT.md for known issues

---

**Time to Complete:** 5-20 minutes (depending on depth)  
**Difficulty:** Beginner-friendly  
**Prerequisites:** Just a web browser!

**Ready? Start with the [5-Minute Quick Test](#5-minute-quick-test) above!** 🚀
