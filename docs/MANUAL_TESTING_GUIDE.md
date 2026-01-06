# 🧪 MANUAL TESTING GUIDE - GoExplorer Live Server

**Server:** http://goexplorer-dev.cloud  
**Status:** Ready for end-to-end testing

---

## QUICK START - TEST THE COMPLETE FLOW IN 5 MINUTES

### Step 1: Visit Homepage (30 seconds)
```
URL: http://goexplorer-dev.cloud/
Expected:
✅ Page loads with blue header
✅ 3 date input fields visible (City, Check-in, Check-out)
✅ Dates show TODAY'S DATE in black text (not invisible!)
✅ Search button at bottom
```

### Step 2: Search Hotels (1 minute)
```
1. Select any city (e.g., "Bangalore")
2. Check-in: Click field, verify date picker appears
3. Check-out: Click field, select tomorrow's date
4. Click "Search Hotels"

Expected:
✅ Hotel list page loads
✅ Hotel cards visible (image + name + rating + price)
✅ At least 2-3 hotels displayed
✅ "View Details & Book" button on each card
```

### Step 3: View Hotel Details (1 minute)
```
1. Click any "View Details & Book" button
2. Page should scroll to show hotel detail

Expected:
✅ Large hotel name at top
✅ Hotel image displays (not gray placeholder!)
✅ Multiple room types listed (Standard, Deluxe, Suite, etc.)
✅ Each room shows: price, occupancy, beds
✅ Room images load on scroll
✅ Booking widget on right side with:
   - Check-in date (prefilled from search)
   - Check-out date (prefilled from search)
   - Room Type dropdown
   - Number of Rooms
   - Number of Guests
   - Guest Name field
   - Email field
   - Phone field
   - Price breakdown
   - "Proceed to Payment" button (or "Login to Book")
```

### Step 4: Start Booking (1 minute)
```
If you see "Login to Book":
1. Click the button
2. Use credentials:
   - Username: goexplorer_dev_admin
   - Password: Thepowerof@9

If you see "Proceed to Payment":
1. Fill in guest name: "Test Guest"
2. Fill in email: "test@example.com"
3. Fill in phone: "9876543210"
4. Select a room type from dropdown
5. Click "Proceed to Payment"

Expected:
✅ Form validates (phone must be 10+ digits)
✅ Success message or redirect to confirmation page
```

### Step 5: Payment Confirmation (1 minute)
```
After booking, you should see:
✅ Booking ID displayed
✅ Hotel name, dates, room type
✅ Total price calculated
✅ "Proceed to Payment" button

DO NOT ACTUALLY PAY (we need to configure Razorpay keys first)
```

---

## DETAILED TEST SCENARIOS

### SCENARIO 1: Date Input Visibility ✅

**Test Date Input Text Visibility**
```
Browser: Desktop Chrome, Firefox, Safari
URL: http://goexplorer-dev.cloud/

Expected Result:
- Open Developer Tools (F12)
- Check the date input elements
- You should see: <input type="date" name="checkin">
- When you click the input, date picker appears
- The date VALUE appears in BLACK TEXT (not invisible/white)
- Both check-in and check-out show dates clearly

CSS that enables this:
input[type="date"] { 
    color: #212529;        /* Dark text */
    background-color: #fff; /* White background */
}
```

**Test Date Persistence (Query Parameters)**
```
1. Go to: http://goexplorer-dev.cloud/
2. Select Check-in: 2026-01-10
3. Select Check-out: 2026-01-12
4. Click "Search Hotels"
5. Observe URL - should contain: ?checkin=2026-01-10&checkout=2026-01-12
6. Go back to homepage
7. Expected: Date fields still show 2026-01-10 and 2026-01-12
```

---

### SCENARIO 2: Hotel Image Loading ✅

**Test Image Display on List Page**
```
URL: http://goexplorer-dev.cloud/hotels/

Expected:
- Each hotel card has an image
- Images are NOT gray/white placeholders
- Images show actual hotel photos
- Common images:
  * Taj Mahal Palace (pink/gold theme)
  * The Leela Palace (modern architecture)
  * The Oberoi Mumbai (high-rise building)

Verify via Browser DevTools:
1. Right-click on image → "Inspect"
2. Check src attribute
3. Should be: /media/hotels/taj_bengal_kolkata_main.jpg
4. Open in new tab → Should load with HTTP 200
```

**Test Image Display on Detail Page**
```
URL: http://goexplorer-dev.cloud/hotels/38/

Expected:
- Large main image visible at top
- Below main image: thumbnail gallery
- Click thumbnails → main image updates
- All images load correctly
- No 404 errors in browser console (F12 → Console tab)
```

---

### SCENARIO 3: Booking Form Completeness ✅

**Test All Form Fields**
```
URL: http://goexplorer-dev.cloud/hotels/38/ (The Leela Palace)

Form fields to verify:
☑ Check-in Date
☑ Check-out Date  
☑ Room Type (dropdown with all room types)
☑ Number of Rooms (numeric input, min=1)
☑ Number of Guests (numeric input, min=1)
☑ Guest Name (text input)
☑ Email (email input)
☑ Phone (tel input, accepts 10+ digits)

Availability Info Box:
☑ Shows "Rooms available: X"
☑ Shows "Best rate: ₹Y/night"
☑ Shows "Source: Internal_Cm"
```

**Test Form Validation**
```
1. Try to submit with Phone = "123" (only 3 digits)
   Expected: Error message "at least 10 digits"

2. Try to submit with invalid email "notanemail"
   Expected: Browser's email validation triggers

3. Try with Check-out before Check-in
   Expected: Browser's date validation or app validation

4. Fill all fields correctly:
   - Check-in: 2026-01-10
   - Check-out: 2026-01-12
   - Room: "Deluxe Room"
   - Rooms: 1
   - Guests: 2
   - Name: "Test User"
   - Email: "test@example.com"
   - Phone: "9876543210"
   Then submit
   Expected: Either success message or redirect to /bookings/{id}/confirm/
```

---

### SCENARIO 4: Booking Confirmation Page ✅

**Test Confirmation Page**
```
URL: http://goexplorer-dev.cloud/bookings/{booking_id}/confirm/

Expected Content:
- Page title: "Booking Confirmation"
- Hotel name: The Leela Palace Bangalore
- Check-in date: 2026-01-10
- Check-out date: 2026-01-12
- Room type: Deluxe Room
- Total nights: 2
- Price breakdown with GST
- Total amount in large, bold text
- "Proceed to Payment" button
- "Cancel Booking" link (optional)

Verify Database State:
1. SSH to server or use Django admin
2. Check: Booking.status = "pending"
3. Check: Booking.inventory_channel = "internal_cm"
4. Check: Booking.lock_id = NULL (no external CM lock)
```

---

### SCENARIO 5: Payment API Status ✅

**Test Payment Endpoints**
```
Test without Auth Token:
1. Open Browser Console (F12 → Console)
2. Paste:
fetch('http://goexplorer-dev.cloud/bookings/api/create-order/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({booking_id: 'test'})
})
.then(r => r.json())
.then(d => console.log(d))

Expected: 403 Forbidden (auth required, which is correct!)

Test with Authenticated User:
1. Login first (see auth section below)
2. Get CSRF token from page source
3. Call endpoint with valid booking_id
Expected: 200 OK with order_id from Razorpay (if keys configured)
         or error if keys not set
```

---

### SCENARIO 6: Channel Manager Integration ✅

**Test Inventory Source Display**
```
URL: http://goexplorer-dev.cloud/hotels/38/

Look for:
- Text showing: "Source: Internal_Cm" or "Source: External_Cm"
- This appears in the availability info box
- Confirms channel manager is tracking inventory

Verify All Hotels Have Inventory Source:
1. Go to: http://goexplorer-dev.cloud/admin/
2. Login: goexplorer_dev_admin / Thepowerof@9
3. Navigate: Hotels → Hotels
4. Check each hotel's "Inventory Source" field
Expected: All 10 hotels have "Internal CM" or "External CM" set
```

**Test Inventory Locking (Advanced)**
```
Database check:
1. SSH: ssh deployer@goexplorer-dev.cloud
2. Password: Thepowerof@9
3. Run: cd /home/deployer/Go_explorer_clear
4. Run: venv/bin/python manage.py shell

Python shell:
from bookings.models import Booking, InventoryLock
from hotels.models import RoomAvailability

# Check a booking's inventory lock
booking = Booking.objects.first()
print(f"Booking {booking.booking_id}:")
print(f"  Status: {booking.status}")
print(f"  Inventory Channel: {booking.inventory_channel}")
print(f"  Lock ID: {booking.lock_id}")

# Check inventory locks table
locks = InventoryLock.objects.all()
print(f"\nTotal locks: {locks.count()}")
for lock in locks[:3]:
    print(f"  Lock {lock.id}: status={lock.status}, expires={lock.expires_at}")
```

---

## AUTHENTICATION GUIDE

### Login with Test Account
```
Admin Account:
- URL: http://goexplorer-dev.cloud/admin/login/
- Username: goexplorer_dev_admin
- Password: Thepowerof@9

Alternative Test Customers:
- Username: customer0, customer1, customer2
- (Check password with team)

After Login:
- You'll see "Proceed to Payment" button on hotel detail pages
- You can create bookings
- API endpoints will return 200 instead of 403
```

### Logout
```
Click: Admin/Logout link in top-right menu
Or navigate to: http://goexplorer-dev.cloud/admin/logout/
```

---

## BROWSER DEVELOPER TOOLS CHECKS

### Console (F12 → Console)
```
Look for:
✅ No JavaScript errors (red X marks)
✅ No 404 errors for images
✅ No CSRF token warnings

Search for errors:
Ctrl+Shift+K → Type "error" → Should find 0 results
```

### Network Tab (F12 → Network)
```
Reload page (Ctrl+Shift+R to clear cache)

Check:
✅ Status 200: Main HTML page
✅ Status 200: All CSS files
✅ Status 200: All JavaScript files
✅ Status 200: Hotel images (/media/hotels/*.jpg)

Red (failed) requests:
❌ Any request ending in .jpg/png with status 404
❌ Any API call with status 500 (server error)
```

### Elements/Inspector (F12 → Inspector)
```
Right-click on element → Inspect

Check HTML structure:
☑ <form id="bookingForm"> exists
☑ <input type="date" id="checkin"> exists
☑ <input type="date" id="checkout"> exists
☑ <select id="room_type"> with options exists
☑ Date input has CSS color: rgb(33, 37, 41) - that's #212529 (dark)
```

---

## TROUBLESHOOTING

### Problem: Dates invisible (white text on white background)

**Solution:**
1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Clear browser cache: Chrome Settings → Clear browsing data
3. Check CSS in Inspector: 
   - F12 → Inspector
   - Right-click on date input
   - Look for: color: rgb(33, 37, 41); background-color: rgb(255, 255, 255);
   - If missing, Nginx/Django may need reload

**Server-side reload:**
```
ssh deployer@goexplorer-dev.cloud
cd /home/deployer/Go_explorer_clear
ps aux | grep gunicorn | grep -v grep | awk '{print $2}' | xargs kill -HUP
```

### Problem: Hotel images show 404 errors

**Solution:**
1. Check in browser console (F12 → Network)
2. Look at failed image requests
3. URL should be: /media/hotels/taj_bengal_kolkata_main.jpg
4. Verify on server:
```
ssh deployer@goexplorer-dev.cloud
curl -I http://goexplorer-dev.cloud/media/hotels/taj_bengal_kolkata_main.jpg
```

Should return: **HTTP/1.1 200 OK**

If 404:
1. Check Django setting: SERVE_MEDIA_FILES=True
2. Check Nginx media alias configuration
3. Verify files exist: `ls -la /home/deployer/Go_explorer_clear/media/hotels/`

### Problem: "Proceed to Payment" button shows "Login to Book"

**Solution:**
This is CORRECT behavior! Only authenticated users can book.

To proceed:
1. Click "Login to Book" button
2. Enter credentials: goexplorer_dev_admin / Thepowerof@9
3. Then "Proceed to Payment" will appear

### Problem: Payment flow doesn't work

**Solution:**
Razorpay keys not configured in .env file. This is expected and needs:
```
# .env file needs:
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_SECRET_KEY=xxxxx

# Then reload gunicorn:
kill -HUP {gunicorn_pid}
```

---

## CHECKLIST FOR VERIFICATION

Print this and check off as you test:

```
Date Inputs:
☐ Homepage shows 3 date inputs
☐ Date text is black, not white/invisible  
☐ Dates persist when page reloads
☐ Query parameters work (?checkin=...&checkout=...)

Hotel Images:
☐ Hotel list page shows images (not gray boxes)
☐ Hotel detail page shows large image
☐ Image gallery thumbnails work
☐ All images HTTP 200 (not 404)

Booking Form:
☐ All 8 form fields present and visible
☐ Room type dropdown populated
☐ Availability info box shows rooms/price/source
☐ Form submits without JavaScript errors

Booking Confirmation:
☐ Confirmation page loads after booking
☐ Shows booking ID, hotel, dates, price
☐ "Proceed to Payment" button visible
☐ Database shows booking created

Payment Integration:
☐ API endpoints return proper status codes (403 if not auth)
☐ Razorpay scripts load (if testing payment)
☐ No JavaScript errors in console

Channel Manager:
☐ Inventory source displayed (Internal_Cm or External_Cm)
☐ Database shows all hotels have inventory_source set
☐ Booking shows inventory_channel field set
```

---

## NEXT PHASE: LIVE PAYMENT TESTING

Once Razorpay keys are configured:

1. Get TEST keys from: https://dashboard.razorpay.com/
2. Add to .env:
   ```
   RAZORPAY_KEY_ID=rzp_test_xxxxx
   RAZORPAY_SECRET_KEY=xxxxx
   ```
3. Reload Gunicorn
4. Test complete flow with:
   - **Test Card:** 4111111111111111
   - **Expiry:** Any future date
   - **CVV:** 123
   - **OTP:** 123456
5. Verify booking.status = "confirmed" after payment

---

**Total testing time: 15-20 minutes**  
**Difficulty: Beginner-friendly**  
**Result: Full end-to-end feature verification**

---

**Questions? Issues?**  
Check: [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)  
or ask your development team!
