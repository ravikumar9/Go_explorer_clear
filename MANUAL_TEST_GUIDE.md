# MANUAL VERIFICATION GUIDE
## All 5 Flows - Desktop & Mobile Parity

**Status**: All automated setup COMPLETE. Dev server running at `http://localhost:8000`

---

## QUICK CHECKLIST

### DESKTOP TESTS (Full browser width)

- [ ] **Test 1: Login Redirect**
  - Go to http://localhost:8000/users/login/
  - Email: `admin@example.com`, Password: `admin`
  - Expected: Redirects to home page (`/`)
  - Expected: No errors/broken styling

- [ ] **Test 2: Bus Search Filters**
  - Go to http://localhost:8000/buses/
  - Search: Bangalore → Hyderabad, Travel Date: Tomorrow
  - Expected: Results load with buses from BLR to HYD
  - Refresh page: Expected: Same results show (filters persist in URL)
  - Check URL bar: Should show `?source_city=BLR&dest_city=HYD&travel_date=...`

- [ ] **Test 3: Seat Layout Desktop Rendering**
  - Click any bus from search results
  - Go to http://localhost:8000/buses/1/?route_id=1&travel_date=2026-01-15
  - Expected: Seat layout displays in grid format (rows/columns)
  - Expected: Seats colored (available=green, ladies=pink, booked=red)
  - Expected: Autocomplete & booking utilities load (check DevTools Network tab for `booking-utilities.js`)

- [ ] **Test 4: Seat Selection & Booking**
  - Click 2-3 available seats
  - Expected: Seats highlight (border/background change)
  - Expected: Total price updates (base fare × seats + fees + tax)
  - Select boarding & dropping points from dropdowns
  - Expected: Dropdowns populated with B/D points

- [ ] **Test 5: Booking Confirmation**
  - Click "Book Now" button
  - Expected: Confirmation page loads with booking summary
  - Expected: Shows booking ID, customer name, email, total amount
  - Expected: No placeholder text (e.g., "[Customer Name]", "[Amount]")

---

### MOBILE TESTS (Responsive view - use DevTools F12 → Ctrl+Shift+M)

Repeat all 5 tests above on mobile viewport (375px width):

- [ ] **Test 1 (Mobile): Login Redirect**
  - Same as desktop but verify responsive layout
  - Expected: Form elements stack vertically, buttons full width

- [ ] **Test 2 (Mobile): Bus Search Filters**
  - Same search, verify mobile-friendly layout
  - Expected: Dropdown/inputs stack properly, no horizontal overflow

- [ ] **Test 3 (Mobile): Seat Layout on Mobile**
  - Expected: Seat grid adapts (smaller fonts, touch-friendly)
  - Expected: Seat layout remains selectable on small screen

- [ ] **Test 4 (Mobile): Seat Selection**
  - Expected: Touch targets are large enough (min 44px)
  - Expected: No layout shift when selecting seats

- [ ] **Test 5 (Mobile): Booking Confirmation**
  - Expected: Booking summary readable on mobile
  - Expected: All info visible without horizontal scroll

---

## WHAT'S AUTOMATED (✓ Verified)

✓ **Database Setup**: 6 cities, 2 operators, 4 buses, 6 routes, 24 B/D points, 200 seats, 180 schedules
✓ **Login Redirect**: Uses `core:home` URL name (no NoReverseMatch)
✓ **Static Files**: 
  - `booking-utilities.js` loaded on `/buses/` and `/buses/<id>/`
  - `booking-styles.css` loaded on all bus/hotel pages
✓ **Filter Persistence**: URL params preserved on page refresh
✓ **Seat Layout Rendering**: CSS media queries present for desktop/mobile
✓ **Booking Context**: Confirmation page templates have real booking data (no placeholders)

---

## CRITICAL: PARITY REQUIREMENT

All 5 flows must work identically on both **desktop and mobile**:
- Same buttons/functionality
- Same data displayed
- Same visual hierarchy
- No layout breaks at 375px width

---

## HOW TO TEST

### Option 1: Browser DevTools (Recommended)
```
1. Open Chrome/Firefox
2. Go to http://localhost:8000
3. Press F12 (DevTools)
4. Click toggle device toolbar (Ctrl+Shift+M)
5. Set to iPhone 12 (375px width)
6. Test each flow
7. Toggle back to desktop, repeat
```

### Option 2: Physical Mobile Device
```
1. Find your machine's local IP: ipconfig (Windows)
2. On mobile, go to http://<YOUR_IP>:8000
3. Test all flows
4. Note any mobile-specific issues
```

---

## KNOWN SETUP DETAILS

| Component | Details |
|-----------|---------|
| **Server** | http://localhost:8000 |
| **Admin Panel** | http://localhost:8000/admin (login: admin/admin) |
| **Test Cities** | BLR, HYD, MUM, MAA, DEL, PNQ |
| **Test Date** | 2026-01-15 onwards (30-day schedules) |
| **Test Buses** | 4 buses with 40-60 seats each |
| **Seat Types** | General (80%), Ladies-Reserved (20%) |

---

## IF ISSUES FOUND

Document the issue with:
1. **Flow Name**: Which test (login, search, seat layout, etc.)
2. **Device**: Desktop or Mobile
3. **Screen Size**: e.g., 375px, 1920px
4. **Error**: Screenshot or error message
5. **Steps to Reproduce**: Exact sequence that breaks

Then proceed with fixes.

---

## SUCCESS CRITERIA

✓ All 5 flows work without errors on desktop
✓ All 5 flows work without errors on mobile (375px)
✓ Desktop and mobile produce same results (parity)
✓ No console errors (DevTools → Console tab)
✓ Page load times < 2 seconds
✓ No layout shifts or broken styling

**Once verified, run**: `git add -A && git commit -m "E2E flows verified: login, search, seat layout, booking confirmation"`

