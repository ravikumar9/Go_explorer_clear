# DevTools Testing Guide – Complete Booking Flow

## Commit: c4290fb
**Date**: January 9, 2026
**Changes**: UX fixes (scrollbars), ladies seat logic, booking redirect, aisle spacing

---

## Testing Environment Setup

### Prerequisites
- Browser: Chrome/Edge with DevTools (F12)
- Navigate to: `https://goexplorer-dev.cloud` (or your dev server)
- Be logged in as a test user

### Before Starting Tests
1. Open Chrome DevTools: **F12**
2. Go to **Console** tab
3. Go to **Network** tab and filter by `Fetch/XHR`
4. Note the URL being tested

---

## Test 1: Hotel Booking Widget – No Nested Scrollbar

### Steps
1. Navigate to: `/hotels/` 
2. Click any hotel → Opens detail page
3. Scroll down to booking widget (right sidebar)

### Check
- [ ] Booking form is **sticky** (stays visible while scrolling content)
- [ ] Form does NOT have its own internal scrollbar
- [ ] All form fields visible without scrolling within the widget
- [ ] Page scrollbar controls entire page scrolling

### DevTools Evidence
- **Console**: No errors about widget overflow
- **Elements**: Inspect `.booking-widget` → should see `max-height: calc(100vh - 120px)` and `overflow-y: auto`

### Pass Criteria
✅ Booking form visible without nested scrolling

---

## Test 2: Seat Layout – Visual Aisle Gap

### Steps
1. Navigate to: `/buses/` → select any bus
2. On bus detail page, scroll to **Seat Layout** section
3. Look at the seat grid

### Check
- [ ] Seats displayed in rows (5 seats per row for seaters)
- [ ] Clear gap between column 3 and column 4 (aisle space)
- [ ] Rows are properly aligned
- [ ] Seats are clickable (no JS errors)

### DevTools Evidence
- **Console**: No `ReferenceError: validateLadiesSeats is not defined`
- **Elements**: Seat rows should show gap element: `.seat-aisle` div between seats 3 and 4

### Pass Criteria
✅ Clear visual aisle, all seats clickable, no console errors

---

## Test 3: Ladies Seat Logic – Gender-Based Selection

### Steps
1. On bus detail page with seat layout visible
2. Select a **Ladies Seat** (pink colored)
3. **Without selecting gender**, check if button is disabled
4. Select gender: **Male** → Check if warning appears
5. Select gender: **Female** → Check if warning disappears and button enables

### Check
- [ ] Ladies seats show pink color (legend confirms)
- [ ] Can SELECT ladies seat without immediate error
- [ ] Gender dropdown causes validation
- [ ] **Male** selected → Warning appears: "Male passengers cannot book ladies seats"
- [ ] **Female** selected → Warning gone, Book button enabled
- [ ] **Other** selected → Warning appears (only Female allowed)

### DevTools Evidence
- **Console**: No `ReferenceError` or `TypeError`
- **Console**: `validateLadiesSeats()` function logs if called
- **Elements**: `.seat.ladies` elements exist with pink background
- **Elements**: Warning div toggles `d-none` class based on gender

### Pass Criteria
✅ Ladies seats only bookable by females, real-time validation works

---

## Test 4: "Book Now" Button – Functional Booking Flow

### Steps

#### 4A: Select Seat → Fill Form → Click Book Now
1. Select **1 seat** (any non-ladies seat if male)
2. Select **Route** (dropdown)
3. Select **Travel Date** (today or later)
4. Enter:
   - Passenger Name: "Test User"
   - Age: "25"
   - Gender: "Male"
   - Boarding Point: (any option)
   - Dropping Point: (any option)
5. Click **"Book Now"** button

### Check
- [ ] Button is NOT disabled after selections
- [ ] Clicking button doesn't just reload page
- [ ] Page redirects to confirmation page (URL: `/bookings/<uuid>/confirm/`)

#### 4B: Confirmation Page Displays Real Data
1. **Wait for redirect** (2-3 seconds)
2. Check confirmation page shows:
   - [ ] Booking ID (UUID format, not "placeholder")
   - [ ] Bus name/operator
   - [ ] Route details (source → destination)
   - [ ] Travel date
   - [ ] Seat numbers selected
   - [ ] Boarding & dropping point names
   - [ ] Total amount (calculated, not $0)
   - [ ] "Proceed to Payment" button present

### DevTools Evidence
- **Network tab**: 
  - POST to `/buses/<id>/book/` → Status 302 (redirect)
  - Followed by GET to `/bookings/<uuid>/confirm/` → Status 200
- **Console**: No POST errors, no 404s
- **Elements**: 
  - Confirm page template shows `{% if booking %}` block (not placeholder block)
  - `booking.booking_id` renders as UUID
  - `booking.bus_details.bus_schedule` shows real data

### Pass Criteria
✅ Book Now → Confirmation shows real booking data

---

## Test 5: Hotel Booking – Same Flow

### Steps
1. Navigate to `/hotels/` → pick a hotel
2. Select:
   - Check-in date
   - Check-out date  
   - Room type
   - Number of rooms: 1
   - Guest info (name, email, phone)
3. Click **"Proceed to Payment"**

### Check
- [ ] Form validates (all fields required)
- [ ] Redirects to `/bookings/<uuid>/confirm/`
- [ ] Confirmation shows:
  - Booking ID
  - Hotel name
  - Room type
  - Check-in/check-out dates
  - Number of nights
  - Total amount
  - Guest details

### DevTools Evidence
- **Network**: POST to `/hotels/<id>/` → 302 redirect to confirmation
- **Console**: No errors

### Pass Criteria
✅ Hotel booking → Confirmation shows real data

---

## Test 6: Static Files Loading – No 404s

### Steps
1. Open DevTools → **Network** tab
2. Reload page (Ctrl+R)
3. Filter by: type **stylesheet** or **script**

### Check
- [ ] `/static/css/booking-styles.css` → Status **200** (not 404)
- [ ] `/static/js/booking-utilities.js` → Status **200** (not 404)
- [ ] All other static assets → Status **200**
- [ ] No red (failed) requests

### Pass Criteria
✅ All static files load successfully

---

## Test 7: Payment Redirect – Booking ID Persistence

### Steps
1. Complete booking flow (Test 4A & 4B)
2. On confirmation page, click **"Proceed to Payment"**
3. Check URL changes to `/bookings/<uuid>/payment/`

### Check
- [ ] URL contains correct booking UUID
- [ ] Payment page displays:
  - Booking ID
  - Amount
  - Razorpay form (or test payment form)
- [ ] No 404 or redirect loops

### DevTools Evidence
- **Network**: GET `/bookings/<uuid>/payment/` → Status 200
- **Console**: No errors

### Pass Criteria
✅ Booking ID persists through payment flow

---

## Final Checklist – "DONE" Definition

Before marking production-ready:

- [ ] **Test 1 PASS**: Hotel widget has no nested scrollbar
- [ ] **Test 2 PASS**: Seat layout shows aisle gap
- [ ] **Test 3 PASS**: Ladies seat logic works (gender-based)
- [ ] **Test 4 PASS**: Bus booking works, confirmation shows real data
- [ ] **Test 5 PASS**: Hotel booking works, confirmation shows real data
- [ ] **Test 6 PASS**: All static files load (no 404s)
- [ ] **Test 7 PASS**: Booking ID persists to payment page
- [ ] **Console**: Zero errors during entire flow
- [ ] **Network**: No failed requests (all 200/302/304)

### Evidence Required
1. Screenshot of Console tab (empty/no errors) during booking
2. Screenshot of Confirmation page showing real booking_id
3. Screenshot of Network tab showing all requests successful

---

## Troubleshooting

### If "Book Now" doesn't work:
- [ ] Check Console for `ReferenceError: validateLadiesSeats is not defined`
- [ ] Check that at least 1 seat is selected (display should show count)
- [ ] Check gender is selected before clicking Book Now
- [ ] Check form POST data in Network tab

### If Confirmation shows "Booking Not Found":
- [ ] Check Network tab: did POST redirect correctly?
- [ ] Check URL has valid UUID
- [ ] Check database has booking created: `python manage.py shell` → `from bookings.models import Booking; Booking.objects.last()`

### If Static files missing (404):
- [ ] Run: `python manage.py collectstatic --noinput`
- [ ] Check `STATIC_ROOT` and `STATIC_URL` in settings.py
- [ ] Verify files exist in `/static/` directory

### If Ladies Seat validation broken:
- [ ] Check Console for errors when gender changes
- [ ] Check Network for any POST errors to seat validation endpoint
- [ ] Reload page to reset form state

---

## Commands for Your Environment

```bash
# Pull latest code
git pull origin main

# Run test data creation
python manage.py create_e2e_test_data --clean

# Start server
python manage.py runserver 0.0.0.0:8000

# Collect static files (production)
python manage.py collectstatic --noinput
```

---

**Next Steps After Testing**:
1. Complete all 7 tests
2. Take screenshots of Console (no errors) + Confirmation (real data)
3. Reply with test results
4. If any FAIL: report exact error in Console/Network
5. Once all PASS: Mark as production-ready

